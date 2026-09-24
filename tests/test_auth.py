from tests.conftest import login


def test_patient_registration_and_login(client):
    response = client.post("/register", data={"full_name":"Asha Patel","email":"asha@example.com","password":"secret1"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data
    response = client.post("/login", data={"email":"asha@example.com","password":"secret1"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Book an Appointment" in response.data


def test_invalid_login_is_rejected(client):
    response = client.post("/login", data={"email":"wrong@example.com","password":"badpass"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_admin_dashboard_requires_admin(client):
    client.post("/register", data={"full_name":"Test Patient","email":"patient@example.com","password":"secret1"})
    client.post("/login", data={"email":"patient@example.com","password":"secret1"})
    response = client.get("/admin", follow_redirects=True)
    assert b"Administrator access is required" in response.data
