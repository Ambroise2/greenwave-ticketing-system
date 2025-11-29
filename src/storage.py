
"""
storage.py - Persistence layer using pickle for GreenWave
"""

import os
import pickle
import uuid
from datetime import datetime, timedelta
from .models import Attendee, Exhibition, Workshop

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ATTENDEES_FILE = os.path.join(DATA_DIR, "attendees.pkl")
WORKSHOPS_FILE = os.path.join(DATA_DIR, "workshops.pkl")
TICKETS_FILE = os.path.join(DATA_DIR, "tickets.pkl")
PAYMENTS_FILE = os.path.join(DATA_DIR, "payments.pkl")
RESERVATIONS_FILE = os.path.join(DATA_DIR, "reservations.pkl")

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def safe_save(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(obj, f)
    os.replace(tmp, path)

def safe_load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "rb") as f:
        return pickle.load(f)

class Storage:
    def __init__(self):
        ensure_data_dir()
        self.attendees = safe_load(ATTENDEES_FILE, {})  # user_id -> Attendee
        self.workshops = safe_load(WORKSHOPS_FILE, {})  # ws_id -> Workshop
        self.tickets = safe_load(TICKETS_FILE, {})      # ticket_id -> Ticket
        self.payments = safe_load(PAYMENTS_FILE, {})    # pay_id -> Payment
        self.reservations = safe_load(RESERVATIONS_FILE, {})  # res_id -> Reservation
        self.exhibitions = {}  # ex_id -> Exhibition
        if not self.workshops:
            self._seed_demo_data()
            self.save_all()

    def _seed_demo_data(self):
        # create 3 exhibitions, each with 3 workshops
        for i, ex in enumerate(["ClimateTech", "Policy", "Community"], start=1):
            ex_id = f"EX{i}"
            self.exhibitions[ex_id] = Exhibition(ex_id, ex)
            for j in range(1,4):
                ws_id = f"WS{ i }{ j }"
                title = f"{ex} Workshop {j}"
                start_time = datetime.now() + timedelta(days=j, hours=i)
                ws = Workshop(ws_id, title, ex_id, capacity=10 + 5*j, start_time=start_time)
                self.workshops[ws_id] = ws
                self.exhibitions[ex_id].workshops.append(ws_id)

    def save_all(self):
        safe_save(ATTENDEES_FILE, self.attendees)
        safe_save(WORKSHOPS_FILE, self.workshops)
        safe_save(TICKETS_FILE, self.tickets)
        safe_save(PAYMENTS_FILE, self.payments)
        safe_save(RESERVATIONS_FILE, self.reservations)

    # helper CRUD
    def add_attendee(self, attendee):
        self.attendees[attendee.user_id] = attendee
        self.save_all()

    def find_attendee_by_email(self, email):
        for a in self.attendees.values():
            if a.email.lower() == email.lower():
                return a
        return None

    def add_ticket(self, ticket):
        self.tickets[ticket.ticket_id] = ticket
        self.save_all()

    def add_payment(self, payment):
        self.payments[payment.pay_id] = payment
        self.save_all()

    def add_reservation(self, reservation):
        self.reservations[reservation.res_id] = reservation
        self.save_all()

    def update_workshop(self, ws):
        self.workshops[ws.ws_id] = ws
        self.save_all()

    def upgrade_ticket(self, ticket_id, ex_id, extra_price=20.0):
        if ticket_id in self.tickets:
            t = self.tickets[ticket_id]
            success = t.upgrade_add_exhibition(ex_id, extra_price)
            if success:
                self.tickets[ticket_id] = t
                self.save_all()
            return success
        return False

    def daily_sales(self):
        by_date = {}
        for p in self.payments.values():
            date_key = p.timestamp.date().isoformat()
            by_date.setdefault(date_key, 0.0)
            by_date[date_key] += p.amount
        return by_date

# Create a singleton storage instance
storage = Storage()
