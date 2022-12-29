from locust import HttpUser, task

from auth.schemas import LoginIn
from chat.schemas import ChatMessage
from chat.service import ChatService


class ChatTests(HttpUser):
    host = "http://127.0.0.1:8000"

    @property
    def users(self):
        return 'chris', 'vitalii'

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        auth = LoginIn(email="jack@example.com", password="stringst")
        response = self.client.post("/api/login", auth.json()).json()
        self.token = {"Authorization": f"Bearer {response['accessToken']}"}
        self.chat_id = ChatService().generate_chat_id(self.users[0], self.users[1])

    @task
    def create_message(self):
        body = ChatMessage(content='hello, bro!')
        self.client.post(f"/api/chat/messages/{self.users[1]}/", data=body.json(), headers=self.token)

    @task
    def get_chats(self):
        self.client.get("/api/chats", headers=self.token)

    @task
    def get_chat_messages(self):
        self.client.get(f"/api/chat/{self.chat_id}/messages/", headers=self.token)
