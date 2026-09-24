from dataclasses import dataclass


@dataclass
class AppointmentRequest:
    doctor_id: int
    appointment_date: str
    appointment_time: str


APPOINTMENT_FEE = 500.00
