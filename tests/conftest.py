import os
import tempfile
import pytest
from app import create_app


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({"TESTING": True, "DATABASE": db_path, "SECRET_KEY": "test-key"})
    yield app
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, email="admin@abc-hospitals.com", password="Admin@123"):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
