import os
import json
import numpy as np
from openai import OpenAI
from neo4j import GraphDatabase

class Llama:
    def __init__(self, llama_url="http://127.0.0.2:8080/v1"):
        """
        Initialize the Llama handler with the llama.cpp server URL.
        :param llama_url: Endpoint of the llama.cpp server.
        """
        self.llama_url = llama_url
        api_key = os.environ["API_KEY"]
        self.client = OpenAI(
            #base_url="http://localhost:8080/v1", 127.0.0.1
            base_url=llama_url,
            api_key = api_key
        )

        neo4j_url = "bolt://172.27.72.27:7687"
        neo4j_user = "neo4j"
        neo4j_password = os.environ["NEO4J_PASSWORD"]
        self.driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_password))
        print("Connected to the database")

    def close(self):
        self.driver.close()

    def create_or_update_person(self, face_id=None, name=None):
            with self.driver.session() as session:
                print("error before here maybe?\n")
                session.run(
                     """
                    MERGE (p:Person {face_id: $face_id})
                    ON CREATE SET p.messages = '[]'
                    ON MATCH SET p.messages = COALESCE(p.messages, '[]')
                    SET p.name = COALESCE($name, p.name)
                    """,
                    face_id=face_id, name=name
                )
                print("error after here maybe?\n")

    def get_person_details(self, face_id):
        """
        Retrieve the details of a person, including the face embedding.
        :param face_id: Unique identifier for the person.
        :return: A dictionary with the person's details, including the face embedding as a NumPy array.
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Person {face_id: $face_id})
                RETURN p.face_id AS face_id, p.name AS name, p.messages AS messages
                """,
                face_id=face_id
            )
            record = result.single()
            if record:
                return {
                    "face_id": record.get("face_id"),
                    "name": record.get("name"),
                    "messages": json.loads(record["messages"]) if record.get("messages") else []
                }
            return None

    def add_message_to_person(self, face_id, user, message):
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (p:Person {face_id: $face_id})
                    RETURN p.messages AS messages
                    """,
                    face_id=face_id
                )
                record = result.single()
                existing_messages = json.loads(record["messages"]) if record and record["messages"] else []
                existing_messages.append({"user": user, "message": message})
                session.run(
                    """
                    MATCH (p:Person {face_id: $face_id})
                    SET p.messages = $updated_messages
                    """,
                    face_id=face_id,
                    updated_messages=json.dumps(existing_messages)
                )
        except Exception as e:
            print("Error in add_message_to_person:")
            traceback.print_exc()
    
    # def add_message_to_person(self, face_id, user, message):
    #     """
    #     Add a new message to the person's conversation history.
    #     :param face_id: Unique identifier for the person.
    #     :param user: The sender of the message ("user" or "llm").
    #     :param message: The content of the message.
    #     """
    #     with self.driver.session() as session:
    #         session.run(
    #             """
    #             MATCH (p:Person {face_id: $face_id})
    #             SET p.messages = CASE
    #                 WHEN p.messages IS NULL THEN $new_message
    #                 ELSE toString(fromJson(p.messages) + $parsed_message)
    #             END
    #             """,
    #             face_id=face_id,
    #             new_message=json.dumps([{"user": user, "message": message}]),
    #             parsed_message={"user": user, "message": message}
    #         )
    #
    def send_to_llama(self, text, face_id):
        """
        Send transcribed text to the llama.cpp server and stream its response.
        :param text: Transcribed text to send.
        :return: Generator yielding streamed responses from the llama.cpp server.
        """
        try:
            person_details = self.get_person_details(face_id)
            if person_details is None:
                self.create_or_update_person(face_id)
                person_details = self.get_person_details(face_id)

            conversation_history = person_details.get("messages", []) if person_details else []

            # Prepare messages for LLM input
            messages = [{"role": "system", "content": "You are a helpful assistant (strictly under 20 words)."}]
            for message in conversation_history:
                role = "user" if message["user"] == "user" else "assistant"
                messages.append({"role": role, "content": message["message"]})
            messages.append({"role": "user", "content": text})

            self.add_message_to_person(face_id, "user", text)

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages= messages,
                temperature=0.7,
                max_tokens=100,
                top_p=0.9,
                stream=True
            )
            # response = self.client.chat.completions.create(
            #     model="gpt-3.5-turbo",  # Model name; can be any string
            #     messages=[
            #         {"role": "system", "content": "You are a helpful assistant (under 20 words)."},
            #         {"role": "user", "content": text}
            #     ],
            #     temperature=0.7,  # Adjusts randomness: 0.0 (deterministic) to 1.0 (more random)
            #     max_tokens=100,   # Maximum number of tokens to generate
            #     top_p=0.9,         # Nucleus sampling: considers tokens that comprise the top P probability mass
            #     stream=True        # Enable streaming responses
            # )
            llm_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    llm_response += content
                    yield content

            # Adding llm response to GraphDatabase
            self.add_message_to_person(face_id, "llm", llm_response)

        except Exception as e:
            print(f"Error sending to llama.cpp server: {e}")
            yield "Error communicating with llama.cpp server"

