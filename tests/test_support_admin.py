from tests.conftest import login


def test_support_message_can_be_submitted(client):
    response = client.post("/support", data={"name":"Asha","email":"asha@example.com","message":"I need help with my appointment."}, follow_redirects=True)
    assert b"support request has been submitted" in response.data


def test_admin_can_add_doctor(client):
    login(client)
    response = client.post("/admin", data={"action":"add_doctor","name":"Dr. New","specialty":"Neurology","availability":"Available"}, follow_redirects=True)
    assert b"Doctor added successfully" in response.data
    assert b"Dr. New" in response.data
