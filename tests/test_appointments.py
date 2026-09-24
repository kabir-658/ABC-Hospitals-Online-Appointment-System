from tests.conftest import login


def create_patient(client):
    client.post("/register", data={"full_name":"Test Patient","email":"patient@example.com","password":"secret1"})
    login(client, "patient@example.com", "secret1")


def test_booking_and_payment_flow(client):
    create_patient(client)
    response = client.post("/appointment", data={"doctor_id":1,"appointment_date":"2030-01-10","appointment_time":"10:00"}, follow_redirects=False)
    assert response.status_code == 302
    payment_url = response.headers["Location"]
    response = client.post(payment_url, data={"method":"Card"}, follow_redirects=True)
    assert b"Payment successful and appointment confirmed" in response.data
    assert b"Confirmed" in response.data


def test_unavailable_slot_is_rejected(client):
    create_patient(client)
    client.post("/appointment", data={"doctor_id":1,"appointment_date":"2030-01-11","appointment_time":"10:00"})
    client.get("/logout")
    client.post("/register", data={"full_name":"Second Patient","email":"second@example.com","password":"secret1"})
    login(client, "second@example.com", "secret1")
    response = client.post("/appointment", data={"doctor_id":1,"appointment_date":"2030-01-11","appointment_time":"10:00"}, follow_redirects=True)
    assert b"This appointment slot is already booked" in response.data
