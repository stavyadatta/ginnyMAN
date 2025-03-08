import os
import json
import traceback
from neo4j import GraphDatabase

from utils import PersonDetails

class _Neo4j:
    def __init__(self, neo4j_url="bolt://172.27.72.27:7687"):
        neo4j_passwd = os.environ["NEO4J_PASSWORD"]
        neo4j_user = "neo4j"
        self.driver = GraphDatabase.driver(neo4j_url, auth=(neo4j_user, neo4j_passwd))
        print("Connected to the database")

    def close(self):
        self.driver.close()

    def read_query(self, query, **params):
        with self.driver.session() as session:
            return session.run(query, **params).data()

    def write_query(self, query, **params):
        with self.driver.session() as session:
            session.run(query, **params)

    def create_or_update_person(self, face_id=None, name=None, state='speak'):
            with self.driver.session() as session:
                session.run(
                     """
                    MERGE (p:Person {face_id: $face_id})
                    ON CREATE SET p.messages = '[]',  p.state = $state
                    ON MATCH SET 
                        p.messages = COALESCE(p.messages, '[]'),
                        p.state = COALESCE($state, p.state)
                    SET p.name = COALESCE($name, p.name)
                    """,
                    face_id=face_id, name=name, state=state
                )
            print("Created a new person")

    def get_person_details(self, face_id) -> PersonDetails:
        """
        Retrieve the details of a person 
        :param face_id: Unique identifier for the person.
        :return: PersonDetails Object
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Person {face_id: $face_id})
                RETURN p.face_id AS face_id, p.name AS name, p.messages AS messages, p.state AS state
                """,
                face_id=face_id
            )
            record = result.single()
            if record:
                return PersonDetails({
                    "face_id": record.get("face_id"),
                    "name": record.get("name"),
                    "messages": json.loads(record["messages"]) if record.get("messages") else [],
                    "state": record.get("state")
                })
            else:
                return PersonDetails()

    def add_message_to_person(self, person_details: PersonDetails):
        messages = person_details.get_attribute("messages")
        face_id = person_details.get_attribute("face_id")
        state = person_details.get_attribute("state")
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MATCH (p:Person {face_id: $face_id})
                    SET p.messages = $updated_messages, p.state=COALESCE($state, p.state)
                    """,
                    face_id=face_id,
                    updated_messages=json.dumps(messages),
                    state=state
                )
        except Exception as e:
            print(f"Error in add_message_to_person: {e}")
            traceback.print_exc()
