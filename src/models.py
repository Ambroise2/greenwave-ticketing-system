
"""
models.py - Domain classes for GreenWave Ticketing System
"""

import hashlib
from datetime import datetime

class User:
    def __init__(self, user_id, name, email, password_plain):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password_hash = hashlib.sha256(password_plain.encode()).hexdigest()

    def check_password(self, pw):
        return hashlib.sha256(pw.encode()).hexdigest() == self.password_hash

class Attendee(User):
    def __init__(self, user_id, name, email, password_plain):
        super().__init__(user_id, name, email, password_plain)
        self.tickets = []           # list of ticket_ids
        self.reservations = []      # list of reservation_ids
        self.purchase_history = []  # list of payment ids

class Admin(User):
    def __init__(self, user_id, name, email, password_plain):
        super().__init__(user_id, name, email, password_plain)

class Exhibition:
    def __init__(self, ex_id, title):
        self.ex_id = ex_id
        self.title = title
        self.workshops = []  # workshop ids

class Workshop:
    def __init__(self, ws_id, title, ex_id, capacity, start_time):
        self.ws_id = ws_id
        self.title = title
        self.ex_id = ex_id
        self.capacity = capacity
        self.start_time = start_time
        self.attendee_ids = []  # reservation ids

    def available_spots(self):
        return max(0, self.capacity - len(self.attendee_ids))

class Ticket:
    def __init__(self, ticket_id, owner_id, price, access_exhibitions):
        self.ticket_id = ticket_id
        self.owner_id = owner_id
        self.price = price
        self.access_exhibitions = list(access_exhibitions)  # list of ex_ids
        self.type = "Generic"

    def upgrade_add_exhibition(self, ex_id, extra_price):
        if ex_id not in self.access_exhibitions:
            self.access_exhibitions.append(ex_id)
            self.price += extra_price
            return True
        return False

class ExhibitionPass(Ticket):
    def __init__(self, ticket_id, owner_id, price, selected_ex_id):
        super().__init__(ticket_id, owner_id, price, [selected_ex_id])
        self.type = "ExhibitionPass"
        self.selected_ex_id = selected_ex_id

class AllAccessPass(Ticket):
    def __init__(self, ticket_id, owner_id, price):
        super().__init__(ticket_id, owner_id, price, [])
        self.access_exhibitions = ["ALL"]
        self.type = "AllAccess"
        self.priority = True
        self.recordings = True

class Reservation:
    def __init__(self, res_id, ticket_id, ws_id, attendee_id, status="CONFIRMED"):
        self.res_id = res_id
        self.ticket_id = ticket_id
        self.ws_id = ws_id
        self.attendee_id = attendee_id
        self.status = status

class Payment:
    def __init__(self, pay_id, ticket_id, amount, method, timestamp=None):
        self.pay_id = pay_id
        self.ticket_id = ticket_id
        self.amount = amount
        self.method = method
        self.timestamp = timestamp or datetime.now()
