import cv2
import glob
import torch
import logging
import argparse
import numpy as np
from pathlib import Path
from queue import Queue
from threading import Thread
from collections import deque
from typing import List, Tuple, Optional
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

class _FaceRecognition:
    """
    A class for face recognition using the InsightFace library.

    This class:
    - Loads existing face embeddings from a database folder.
    - Detects faces and generates embeddings for images provided as numpy arrays.
    - Compares the generated embedding against known embeddings using cosine similarity.
    - If no match is found (based on a threshold), it can save the new face into the database
      (but only when explicitly instructed, not by default).
    """

    def __init__(self, 
                 db_dir: str = "/workspace/database/face_db",
                 model_name: str = "buffalo_l",
                 recognition_threshold: float = 0.55):
        """
        Initialize the FaceRecognition class.

        Args:
            db_dir (str): Directory path for face database.
            model_name (str): InsightFace model name.
            recognition_threshold (float): Threshold for considering a face as known.
        """
        self.db_dir = Path(db_dir)
        self.recognition_threshold = recognition_threshold
        self.model_name = model_name

        # Ensure database directory exists
        self._ensure_db_directory()

        # Initialize face analysis model
        self.app = self._initialize_face_analysis()

        # Load database embeddings
        self.known_ids, self.known_embeddings = self._load_database()

        self.face_img_queue = Queue(maxsize=15)
        self.face_id_queue = deque(maxlen=15)
        self.save_img_queue = deque(maxlen=15)
        self.face_embedding_queue = deque(maxlen=15)

        face_recognition_thread = Thread(
            target=self._face_recognition_on_queue,
            daemon=True
        )

        # face_recognition_thread.start()

    def add2face_img_queue(self, image):
        self.face_img_queue.put(image)

    def _ensure_db_directory(self):
        """Ensure that the database directory exists."""
        if not self.db_dir.exists():
            self.db_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_face_analysis(self) -> FaceAnalysis:
        """Initialize the InsightFace FaceAnalysis object and load models."""
        providers = [('CUDAExecutionProvider', {"device_id": 0}), 'CPUExecutionProvider'] \
            if torch.cuda.is_available() else ['CPUExecutionProvider']
        app = FaceAnalysis(name=self.model_name, providers=providers)
        app.prepare(ctx_id=0 if torch.cuda.is_available() else -1)
        return app

    def _load_database(self) -> Tuple[List[str], np.ndarray]:
        """
        Load the known face embeddings and IDs from the database directory.

        Returns:
            Tuple[List[str], np.ndarray]: A list of face IDs and a numpy array of their embeddings.
        """
        embedding_files = glob.glob(str(self.db_dir / "*.npy"))
        known_ids = []
        known_embeddings = []

        for ef in embedding_files:
            face_id = Path(ef).stem  # filename without extension
            emb = np.load(ef)
            known_ids.append(face_id)
            known_embeddings.append(emb)

        if known_embeddings:
            known_embeddings = np.vstack(known_embeddings)
        else:
            known_embeddings = np.array([])

        return known_ids, known_embeddings

    def _get_embedding(self, img: np.ndarray) -> np.ndarray:
        """
        Given an image array, detect the face, and generate a face embedding.

        Args:
            img (np.ndarray): The image array.

        Returns:
            np.ndarray: The face embedding vector of shape (1, embedding_dim).
        """
        faces = self.app.get(img)
        if len(faces) == 0:
            raise ValueError("No face detected in the given image.")

        face = faces[0]
        embedding = face.embedding
        embedding = embedding.reshape(1, -1)  # shape: (1, embedding_dim)
        return embedding

    def _match_face(self, embedding: np.ndarray) -> Optional[str]:
        """
        Match the given embedding against known embeddings.

        Args:
            embedding (np.ndarray): The face embedding to match.

        Returns:
            Optional[str]: The matched face ID if found, otherwise None.
        """
        if self.known_embeddings.size == 0:
            return None

        # Compute cosine similarity
        sim = cosine_similarity(embedding, self.known_embeddings)
        best_match_idx = np.argmax(sim)
        best_score = sim[0, best_match_idx]

        # Threshold check (closer to 1 is more similar)
        # We interpret "recognition_threshold" as the maximum distance from 1 
        # allowed. i.e. if best_score >= (1 - threshold) => recognized
        if best_score >= (1 - self.recognition_threshold):
            return self.known_ids[best_match_idx]
        else:
            return None

    def _save_new_face(self, embedding: np.ndarray, img: np.ndarray, save_img=True) -> str:
        """
        Save a new face to the database (embedding and optionally the face image).

        Returns:
            str: The ID of the newly saved face.
        """
        # Generate a new unique ID
        new_id = self._generate_new_face_id()

        # Save embedding to disk
        np.save(self.db_dir / f"{new_id}.npy", embedding)

        # Update known faces in memory
        self.known_ids.append(new_id)
        if self.known_embeddings.size == 0:
            self.known_embeddings = embedding
        else:
            self.known_embeddings = np.vstack([self.known_embeddings, embedding])
        
        # Optionally save the face image
        if save_img:
            out_path = self.db_dir / f"{new_id}.png"
            cv2.imwrite(str(out_path), img)

        return new_id

    def _generate_new_face_id(self) -> str:
        """
        Generate a unique face ID by counting existing IDs.

        Returns:
            str: A new face ID, for example 'face_1', 'face_2', etc.
        """
        current_ids = [int(x.replace("face_", "")) 
                       for x in self.known_ids if x.startswith("face_")]
        next_id_num = (max(current_ids) + 1) if current_ids else 1
        return f"face_{next_id_num}"

    ############################################################################
    #               Key Changes: Separate "recognize" vs. "enroll"             #
    ############################################################################
    def recognize_face_no_enroll(self, img: np.ndarray) -> Tuple[Optional[str], np.ndarray]:
        """
        Attempt to recognize the face in the image but DO NOT enroll new faces.
        This method returns the recognized ID (or None if unknown) AND the embedding.

        Returns:
            (face_id, embedding)
        """
        embedding = self._get_embedding(img)
        face_id = self._match_face(embedding)
        return face_id, embedding

    def enroll_face(self, embedding: np.ndarray, img: np.ndarray) -> str:
        """
        Explicitly enroll a new face into the database using the given embedding and image.

        Returns:
            str: the newly generated face ID
        """
        return self._save_new_face(embedding, img, save_img=True)

    def _face_recognition_on_queue(self):
        while True:
            img = self.face_img_queue.get()

            try:
                recognized_id, emb = self.recognize_face_no_enroll(img)
            except ValueError as e:
                continue

            self.face_id_queue.append(recognized_id)
            self.face_embedding_queue.append(emb)
            self.save_img_queue.append(img)

    ############################################################################
    #            Modified method that does the voting over 10 frames           #
    ############################################################################

    def get_most_frequent_face_id(self) -> Optional[str]:
        """
        Process up to the last 10 images in the queue, attempt to recognize each face
        WITHOUT immediately enrolling any new face. If the final "winner" is None or
        if None-count is strictly greater than the most frequent recognized ID count,
        then enroll as a new face.

        Returns:
            Optional[str]: The most frequent recognized face ID or a newly enrolled ID.
        """
        recent_images = list(self.save_img_queue)[-10:]
        face_ids = list(self.face_id_queue)[-10:]
        embeddings = list(self.face_embedding_queue)[-10:]

        if len(face_ids) == 0:
            return None

        # 2) Count how often each ID appears, plus how many are None
        from collections import Counter
        counter = Counter(face_ids)  # e.g., {face_1: 3, face_2: 1, None: 6}
        none_count = counter[None]
        del counter[None]  # remove None from the recognized-IDs dict if it exists

        if len(counter) == 0:
            # There were no recognized IDs at all => everything was None
            most_frequent_id = None
            max_freq = 0
        else:
            # Identify the recognized ID with the highest frequency
            most_frequent_id, max_freq = max(counter.items(), key=lambda x: x[1])  # e.g. ("face_1", 3)

        # 3) If the number of None is strictly greater than the max recognized frequency,
        #    treat the result as "new/unknown" face.
        if none_count > max_freq:
            logging.info(f"None-count ({none_count}) > recognized-count ({max_freq}). "
                        "Treating as new face.")
            most_frequent_id = None

        # 4) If the final voted ID is None => truly unknown => we enroll as new face
        if most_frequent_id is None:
            # Enroll a new face from one of the unknown instances (e.g., the last unknown)
            for i in reversed(range(len(face_ids))):
                if face_ids[i] is None and embeddings[i] is not None:
                    new_face_id = self.enroll_face(embeddings[i], recent_images[i])
                    logging.info(f"No known face found in the last 10 images. "
                                f"Enrolled new face: {new_face_id}")
                    return new_face_id
            # If we never found a valid unknown embedding, just return None
            return None

        # 5) Otherwise, return the recognized majority face
        logging.info(f"Most frequent recognized ID is: {most_frequent_id} "
                    f"(count={max_freq}, none_count={none_count})")
        return most_frequent_id

    def get_face_box(self, img: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect the face in the image and return the bounding box.

        Args:
            img (np.ndarray): The input image array (e.g., from cv2.imread).

        Returns:
            Optional[Tuple[int, int, int, int]]: Bounding box (x, y, w, h) if a face is detected, else None.
        """
        bboxes, _ = self.app.det_model.detect(img, max_num=0, metric='default')
        if bboxes.shape[0] == 0:
            # logging.warning("No person found")
            return None

        first_bbox = bboxes[0, 0:4].astype(int)
        return tuple(first_bbox)

def main():
    parser = argparse.ArgumentParser(description="Face recognition embedding extractor")
    parser.add_argument("--img_path", type=str, help="Path to the input image")
    parser.add_argument("--output_dir", type=str, default="./output_embeddings", help="Directory to save the embedding")
    args = parser.parse_args()

    img_path = Path(args.img_path)
    if not img_path.exists():
        logging.error(f"Image file not found: {img_path}")
        return

    img = cv2.imread(str(img_path))
    if img is None:
        logging.error("Failed to read image.")
        return

    recognizer = _FaceRecognition()
    import time
    start_time = time.time()
    try:
        embedding = recognizer._get_embedding(img)
    except ValueError as e:
        logging.error(f"Face detection failed: {e}")
        return
    end_time = time.time()
    print(f"Batch prediction took {(end_time - start_time) * 1000:.2f} ms")
    exit()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    embedding_path = output_dir / f"{img_path.stem}_embedding.npy"
    np.save(embedding_path, embedding)

    print(f"Embedding saved at: {embedding_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

