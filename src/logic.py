
"""
logic.py - Business logic functions for GreenWave
"""
import uuid
from . import storage
from .models import Attendee, Ticket, ExhibitionPass, AllAccessPass, Reservation, Payment

def create_account(name, email, password):
    if storage.storage.find_attendee_by_email(email):
        raise ValueError("Email already registered.")
    uid = "U"+uuid.uuid4().hex[:8]
    att = Attendee(uid, name, email, password)
    storage.storage.add_attendee(att)
    return att

def simulate_payment(ticket, method="Card"):
    pay_id = "P"+uuid.uuid4().hex[:8]
    payment = Payment(pay_id, ticket.ticket_id, ticket.price, method)
    storage.storage.add_payment(payment)
    owner = storage.storage.attendees.get(ticket.owner_id)
    if owner:
        owner.purchase_history.append(payment.pay_id)
        storage.storage.save_all()
    return payment

def purchase_ticket(attendee_id, ticket_type, selected_ex_ids=None):
    att = storage.storage.attendees.get(attendee_id)
    if not att:
        raise ValueError("Attendee not found.")
    tid = "T"+uuid.uuid4().hex[:8]
    if ticket_type == "Exhibition":
        if not selected_ex_ids:
            raise ValueError("No exhibition selected.")
        ticket = ExhibitionPass(tid, attendee_id, price=50.0 * len(selected_ex_ids), selected_ex_id=selected_ex_ids[0])
        for ex in selected_ex_ids[1:]:
            ticket.upgrade_add_exhibition(ex, 50.0)
    elif ticket_type == "AllAccess":
        ticket = AllAccessPass(tid, attendee_id, price=150.0)
    else:
        raise ValueError("Unknown ticket type.")
    storage.storage.add_ticket(ticket)
    att.tickets.append(ticket.ticket_id)
    storage.storage.save_all()
    payment = simulate_payment(ticket, method="Card")
    return ticket, payment

def reserve_workshop(attendee_id, ticket_id, ws_id):
    att = storage.storage.attendees.get(attendee_id)
    if not att:
        raise ValueError("attendee not found")
    ticket = storage.storage.tickets.get(ticket_id)
    if not ticket:
        raise ValueError("ticket not found")
    ws = storage.storage.workshops.get(ws_id)
    if not ws:
        raise ValueError("workshop not found")
    if ws.available_spots() <= 0:
        raise OverflowError("No seats available.")
    if "ALL" not in ticket.access_exhibitions and ws.ex_id not in ticket.access_exhibitions:
        raise PermissionError("Ticket does not allow access to this exhibition's workshops.")
    rid = "R"+uuid.uuid4().hex[:8]
    res = Reservation(rid, ticket.ticket_id, ws_id, attendee_id)
    storage.storage.add_reservation(res)
    ws.attendee_ids.append(rid)
    storage.storage.update_workshop(ws)
    att.reservations.append(rid)
    storage.storage.save_all()
    return res

def cancel_reservation(res_id):
    res = storage.storage.reservations.get(res_id)
    if not res:
        raise ValueError("reservation not found")
    ws = storage.storage.workshops.get(res.ws_id)
    if ws and res_id in ws.attendee_ids:
        ws.attendee_ids.remove(res_id)
        storage.storage.update_workshop(ws)
    att = storage.storage.attendees.get(res.attendee_id)
    if att and res_id in att.reservations:
        att.reservations.remove(res_id)
    res.status = "CANCELLED"
    storage.storage.reservations[res_id] = res
    storage.storage.save_all()
    return res
