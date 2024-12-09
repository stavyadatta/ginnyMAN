import os
import cv2
import glob
import torch
import numpy as np
from typing import List, Tuple
from pathlib import Path
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

class FaceRecognition:
    """
    A class for face recognition using the InsightFace library.

    This class:
    - Loads existing face embeddings from a database folder.
    - Detects faces and generates embeddings for images provided as numpy arrays.
    - Compares the generated embedding against known embeddings using cosine similarity.
    - If no match is found (based on a threshold), it saves the new face into the database.
    
    GPU usage:
    - By default, attempts to use GPU if available for both detection and embedding.
    """

    def __init__(self, 
                 db_dir: str = "/workspace/database/face_db",
                 model_name: str = "buffalo_l",
                 recognition_threshold: float = 0.3):
        """
        Initialize the FaceRecognition class.

        Args:
            db_dir (str): Directory path for face database. Defaults to './face_db'.
            model_name (str): InsightFace model name. Defaults to 'buffalo_l'.
            recognition_threshold (float): Threshold for considering a face as known.
                                            Lower means stricter matching.
                                            Default is 0.3.
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

    def recognize_face(self, img: np.ndarray) -> str:
        """
        Recognize the face in the given image (as a numpy array).

        Steps:
        - Generate embedding for the face in the image.
        - Compare with known embeddings using cosine similarity.
        - If a match is found above the threshold, return the known face ID.
        - Else, save this face as a new ID.

        Args:
            img (np.ndarray): The input image array (e.g., from cv2.imread).

        Returns:
            str: The ID of the recognized face or the newly assigned ID.
        """
        embedding = self._get_embedding(img)
        face_id = self._match_face(embedding)

        if face_id is None:
            face_id = self._save_new_face(embedding, img, save_img=True)

        return face_id

    def _ensure_db_directory(self):
        """
        Ensure that the database directory exists.
        If not, create it.
        """
        if not self.db_dir.exists():
            self.db_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_face_analysis(self) -> FaceAnalysis:
        """
        Initialize the InsightFace FaceAnalysis object and load models.
        Attempt to use GPU if available.

        Returns:
            FaceAnalysis: The initialized and prepared face analysis object.
        """
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if torch.cuda.is_available() else ['CPUExecutionProvider']
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
            np.ndarray: The face embedding vector.
        """
        faces = self.app.get(img)
        if len(faces) == 0:
            raise ValueError("No face detected in the given image.")

        face = faces[0]
        embedding = face.embedding
        embedding = embedding.reshape(1, -1)  # shape: (1, embedding_dim)
        return embedding

    def _match_face(self, embedding: np.ndarray) -> str:
        """
        Match the given embedding against known embeddings.

        Args:
            embedding (np.ndarray): The face embedding to match.

        Returns:
            str: The matched face ID if found, otherwise None.
        """
        if self.known_embeddings.size == 0:
            return None

        # Compute cosine similarity
        sim = cosine_similarity(embedding, self.known_embeddings)
        best_match_idx = np.argmax(sim)
        best_score = sim[0, best_match_idx]

        # Threshold check: similarity close to 1 means more similar
        # Using threshold: if sim is high enough (1 - threshold), consider matched
        if best_score >= (1 - self.recognition_threshold):
            return self.known_ids[best_match_idx]
        else:
            return None

    def _save_new_face(self, embedding: np.ndarray, img: np.ndarray, save_img=False) -> str:
        """
        Save a new face to the database.

        Returns:
            str: The ID of the newly saved face.
        """
        # Generate a new unique ID
        new_id = self._generate_new_face_id()

        # Save embedding to disk
        np.save(self.db_dir / f"{new_id}.npy", embedding)

        # Update known faces
        self.known_ids.append(new_id)
        if self.known_embeddings.size == 0:
            self.known_embeddings = embedding
        else:
            self.known_embeddings = np.vstack([self.known_embeddings, embedding])
        
        if save_img:
            cv2.imwrite(str((self.db_dir / f"{new_id}.png").absolute()), img)
        return new_id

    def _generate_new_face_id(self) -> str:
        """
        Generate a unique face ID by counting existing IDs.

        Returns:
            str: A new face ID, for example 'face_1', 'face_2', etc.
        """
        current_ids = [int(x.replace("face_", "")) for x in self.known_ids if x.startswith("face_")]
        next_id_num = (max(current_ids) + 1) if current_ids else 1
        return f"face_{next_id_num}"

if __name__ == "__main__":
    # Initialize the FaceRecognition system
    face_recognition = FaceRecognition()

    # Load the first image and save its face
    img1_path = "/workspace/database/stavya_imgs/20240325_135719.jpg"
    img1 = cv2.imread(img1_path)
    if img1 is None:
        raise ValueError(f"Image not found: {img1_path}")
    print(f"Processing the first image: {img1_path}")
    face_id_1 = face_recognition.recognize_face(img1)
    print(f"Saved face ID for the first image: {face_id_1}")

    # Load the second image and compare
    img2_path = "/workspace/database/stavya_imgs/20240701_122416.jpg"
    img2 = cv2.imread(img2_path)
    if img2 is None:
        raise ValueError(f"Image not found: {img2_path}")
    print(f"Processing the second image: {img2_path}")
    face_id_2 = face_recognition.recognize_face(img2)
    if face_id_1 == face_id_2:
        print("The second image matches the face from the first image.")
    else:
        print("The second image does not match the face from the first image.")

    # Load the third image and compare
    img3_path = "/workspace/database/rob_imgs/IMG-20200411-WA0008.jpeg"
    img3 = cv2.imread(img3_path)
    if img3 is None:
        raise ValueError(f"Image not found: {img3_path}")
    print(f"Processing the third image: {img3_path}")
    face_id_3 = face_recognition.recognize_face(img3)
    if face_id_1 == face_id_3:
        print("The third image matches the face from the first image.")
    else:
        print("The third image does not match the face from the first image.")

