import os
import logging
from datetime import datetime

import flet as ft
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Session, TrainingSet, TrainingMessage, SessionMessage
from training import client, training_messages

# Configure logging
logging.basicConfig(filename='application.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(message)s')

# Read the database URL from the environment variable
DATABASE_URL = os.getenv("DULE_DB_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_training_set() -> TrainingSet:
    session = SessionLocal()
    try:
        # Check if the TrainingSet with name "Dorćolac" exists
        training_set = session.query(TrainingSet).filter_by(name="Dorćolac").first()

        if not training_set:
            # Create new TrainingSet with name "Dorćolac"
            training_set = TrainingSet(name="Dorćolac")
            session.add(training_set)
            session.commit()  # Commit to get the ID of the new TrainingSet

            # Add all TrainingMessages from training_messages
            for message in training_messages:
                role = message["role"]
                content = message["content"][0]["text"]
                training_message = TrainingMessage(
                    training_set_id=training_set.id,
                    role=role,
                    content=content
                )
                session.add(training_message)

            # Commit all TrainingMessages to the database
            session.commit()

        return training_set
    finally:
        session.close()

def create_session(training_set: TrainingSet) -> Session:
    session = SessionLocal()
    try:
        # Create new Session with the given TrainingSet and current date and time
        new_session = Session(
            training_set_id=training_set.id,
            start_time=datetime.now()
        )
        session.add(new_session)
        session.commit()  # Commit to get the ID of the new Session
        session.refresh(new_session)  # Refresh to get the updated new_session object
        return new_session
    finally:
        session.close()

def main(page: ft.Page):
    try:
        def greeting() -> str:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=training_messages + [generate_message("system", "pozdravi Duleta")],
                temperature=1,
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                response_format={
                    "type": "text"
                })

            greeting_message = response.choices[0].message.content

            session = SessionLocal()
            # Store user message in SessionMessage
            user_session_message = SessionMessage(
                session_id=current_db_session.id,
                role="assistant",
                content=greeting_message,
                timestamp=datetime.now()
            )
            session.add(user_session_message)
            session.commit()

            return f"Dorćolac: {greeting_message}"

        def generate_message(role: str, text: str):
            return {
                "role": role,
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }

        def send_message(e):
            session = SessionLocal()
            try:
                user_message = message_input.value

                # Store user message in SessionMessage
                user_session_message = SessionMessage(
                    session_id=current_db_session.id,
                    role="user",
                    content=user_message,
                    timestamp=datetime.now()
                )
                session.add(user_session_message)
                session.commit()

                assistant_message = get_response(user_message)

                # Store assistant message in SessionMessage
                assistant_session_message = SessionMessage(
                    session_id=current_db_session.id,
                    role="assistant",
                    content=assistant_message,
                    timestamp=datetime.now()
                )
                session.add(assistant_session_message)
                session.commit()

                list_view.controls.append(ft.Text(value=f"Dule: {user_message}"))
                list_view.controls.append(ft.Text(value=f"Dorćolac: {assistant_message}"))
                message_input.value = ""
                page.update()
            except Exception as e:
                logging.error("Error in send_message: %s", e)
                page.add(ft.Text(value="Application Error, check logs"))
            finally:
                session.close()

        def get_response(user_message):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=training_messages + [generate_message("user", user_message)],
                temperature=1,
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                response_format={
                    "type": "text"
                })
            assistant_message = response.choices[0].message.content
            return assistant_message

        current_training_set = init_training_set()
        current_db_session = create_session(current_training_set)

        # UI elements
        list_view = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
        list_view.controls.append(ft.Text(value=greeting()))
        message_input = ft.TextField(label="Unesi poruku", multiline=True)
        send_button = ft.ElevatedButton(text="Pošalji", on_click=send_message)

        # Add elements to the page
        page.add(
            list_view,
            ft.Column(
                [
                    message_input,
                    send_button
                ],
                alignment=ft.MainAxisAlignment.END
            )
        )
    except Exception as e:
        logging.error("Error in main: %s", e)
        page.add(ft.Text(value="Application Error, check logs"))

# Run the Flet application
ft.app(target=main)