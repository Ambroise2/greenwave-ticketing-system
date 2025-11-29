
"""
gui.py - Tkinter GUI for GreenWave Ticketing System
Run with: python main.py
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from . import storage
from . import logic

class GreenWaveApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GreenWave Ticketing System")
        self.geometry("900x600")
        self.active_user = None
        self.create_widgets()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(side="top", fill="x", padx=8, pady=8)
        ttk.Button(top, text="Login / Create Account", command=self.login_window).pack(side="left")
        ttk.Button(top, text="Admin Login", command=self.admin_login).pack(side="left")
        ttk.Button(top, text="Show Exhibitions", command=self.show_exhibitions).pack(side="left")
        ttk.Button(top, text="My Account", command=self.my_account).pack(side="left")
        ttk.Button(top, text="Exit", command=self.destroy).pack(side="right")
        self.main = ttk.Frame(self)
        self.main.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Label(self.main, text="Welcome to GreenWave Conference Ticketing", font=("Helvetica", 16)).pack(pady=20)
        ttk.Label(self.main, text="Use the buttons above to login, view exhibitions, purchase tickets, and reserve workshops.").pack()

    def admin_login(self):
        email = simpledialog.askstring("Admin Login", "Enter admin email:")
        pw = simpledialog.askstring("Admin Login", "Enter password:", show="*")
        if email == "admin@greenwave" and pw == "adminpass":
            self.active_user = None
            AdminDashboard(self)
        else:
            messagebox.showerror("Admin Login", "Invalid admin credentials. For demo use admin@greenwave / adminpass")

    def login_window(self):
        LoginWindow(self)

    def show_exhibitions(self):
        ExhibitionsWindow(self)

    def my_account(self):
        if not self.active_user or not isinstance(self.active_user, type(storage.storage.attendees.get(next(iter(storage.storage.attendees))) if storage.storage.attendees else None)):
            messagebox.showinfo("Account", "You must login as an attendee first.")
            return
        AttendeeWindow(self, self.active_user)

class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Login / Create Account")
        self.geometry("400x300")
        ttk.Label(self, text="Email").pack(pady=4)
        self.email_entry = ttk.Entry(self)
        self.email_entry.pack(pady=4)
        ttk.Label(self, text="Password").pack(pady=4)
        self.pw_entry = ttk.Entry(self, show="*")
        self.pw_entry.pack(pady=4)
        ttk.Button(self, text="Login", command=self.do_login).pack(pady=6)
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=6)
        ttk.Label(self, text="Or create a new account").pack(pady=4)
        ttk.Button(self, text="Create Account", command=self.create_account).pack(pady=4)
        self.parent = parent

    def do_login(self):
        email = self.email_entry.get().strip()
        pw = self.pw_entry.get().strip()
        user = storage.storage.find_attendee_by_email(email)
        if not user:
            messagebox.showerror("Login", "User not found.")
            return
        if user.check_password(pw):
            messagebox.showinfo("Login", f"Welcome back, {user.name}")
            self.parent.active_user = user
            self.destroy()
        else:
            messagebox.showerror("Login", "Incorrect password.")

    def create_account(self):
        name = simpledialog.askstring("Create Account", "Full name:")
        email = simpledialog.askstring("Create Account", "Email:")
        pw = simpledialog.askstring("Create Account", "Choose a password:", show="*")
        try:
            att = logic.create_account(name, email, pw)
            messagebox.showinfo("Account", f"Account created for {att.name}. You may now login.")
        except Exception as e:
            messagebox.showerror("Create Account", str(e))

class ExhibitionsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Exhibitions and Workshops")
        self.geometry("850x500")
        self.parent = parent
        self.build()

    def build(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True)
        for ex in storage.storage.exhibitions.values():
            lab = ttk.Label(frame, text=f"{ex.title} ({ex.ex_id})", font=("Helvetica", 12, "bold"))
            lab.pack(anchor="w", pady=(8,0))
            for ws_id in ex.workshops:
                ws = storage.storage.workshops.get(ws_id)
                line = f"  [{ws.ws_id}] {ws.title} - Starts: {ws.start_time.strftime('%Y-%m-%d %H:%M')} - Spots: {ws.available_spots()}/{ws.capacity}"
                row = ttk.Frame(frame)
                row.pack(fill="x", padx=8, pady=2)
                ttk.Label(row, text=line).pack(side="left")
                ttk.Button(row, text="Reserve", command=lambda w=ws: self.reserve(w)).pack(side="right")
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=10)

    def reserve(self, ws):
        if not self.parent.active_user or not hasattr(self.parent.active_user, "tickets"):
            messagebox.showinfo("Reserve", "You must login as an attendee first.")
            return
        user = self.parent.active_user
        if not user.tickets:
            messagebox.showinfo("Reserve", "No tickets found. Buy a ticket first.")
            return
        ticket_id = user.tickets[0]
        try:
            res = logic.reserve_workshop(user.user_id, ticket_id, ws.ws_id)
            messagebox.showinfo("Reservation", f"Reserved {ws.title} ({res.res_id})")
        except Exception as e:
            messagebox.showerror("Reservation", str(e))

class AttendeeWindow(tk.Toplevel):
    def __init__(self, parent, attendee):
        super().__init__(parent)
        self.title(f"My Account - {attendee.name}")
        self.geometry("800x500")
        self.attendee = attendee
        self.build()

    def build(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Label(frame, text=f"Hello, {self.attendee.name}", font=("Helvetica", 14)).pack(anchor="w")
        ttk.Label(frame, text="Tickets:", font=("Helvetica", 12, "underline")).pack(anchor="w", pady=(8,0))
        for tid in self.attendee.tickets:
            t = storage.storage.tickets.get(tid)
            ttk.Label(frame, text=f" - {t.ticket_id} | Type: {t.type} | Price: ${t.price:.2f} | Access: {t.access_exhibitions}").pack(anchor="w")
            ttk.Button(frame, text="Upgrade Ticket", command=lambda tid=tid: self.upgrade_ticket(tid)).pack(anchor="e", pady=2)
        ttk.Label(frame, text="Reservations:", font=("Helvetica", 12, "underline")).pack(anchor="w", pady=(8,0))
        for rid in self.attendee.reservations:
            r = storage.storage.reservations.get(rid)
            ws = storage.storage.workshops.get(r.ws_id)
            ttk.Label(frame, text=f" - {r.res_id} | {ws.title} | Status: {r.status}").pack(anchor="w")
            ttk.Button(frame, text="Cancel", command=lambda rid=rid: self.do_cancel(rid)).pack(anchor="e", pady=2)
        ttk.Button(frame, text="Purchase Ticket", command=self.do_purchase).pack(pady=8)

    def do_purchase(self):
        choice = simpledialog.askstring("Ticket Purchase", "Ticket type (Exhibition/AllAccess):")
        if not choice:
            return
        if choice == "Exhibition":
            ex_id = simpledialog.askstring("Select Exhibition", f"Enter exhibition id from: {list(storage.storage.exhibitions.keys())}")
            if not ex_id or ex_id not in storage.storage.exhibitions:
                messagebox.showerror("Purchase", "Invalid exhibition id.")
                return
            ticket, payment = logic.purchase_ticket(self.attendee.user_id, "Exhibition", selected_ex_ids=[ex_id])
        elif choice == "AllAccess":
            ticket, payment = logic.purchase_ticket(self.attendee.user_id, "AllAccess")
        else:
            messagebox.showerror("Purchase", "Unknown ticket type.")
            return
        messagebox.showinfo("Purchase", f"Ticket {ticket.ticket_id} purchased. Payment {payment.pay_id}. Please refresh account window.")
        self.destroy()

    def upgrade_ticket(self, ticket_id):
        ex_id = simpledialog.askstring("Upgrade ticket", f"Enter exhibition id to add: {list(storage.storage.exhibitions.keys())}")
        if not ex_id:
            return
        ok = storage.storage.upgrade_ticket(ticket_id, ex_id, extra_price=40.0)
        if ok:
            messagebox.showinfo("Upgrade", "Ticket upgraded successfully.")
            self.destroy()
        else:
            messagebox.showerror("Upgrade", "Upgrade failed (maybe already included).")

    def do_cancel(self, rid):
        try:
            logic.cancel_reservation(rid)
            messagebox.showinfo("Cancel", "Reservation cancelled.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Cancel", str(e))

class AdminDashboard(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Admin Dashboard")
        self.geometry("900x600")
        self.build()

    def build(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Label(frame, text="Admin Dashboard", font=("Helvetica", 16)).pack()
        sales = storage.storage.daily_sales()
        ttk.Label(frame, text="Daily Sales:").pack(anchor="w", pady=(8,0))
        for d, amt in sales.items():
            ttk.Label(frame, text=f" - {d} : ${amt:.2f}").pack(anchor="w")
        ttk.Label(frame, text="Workshop capacities:").pack(anchor="w", pady=(8,0))
        for ws in storage.storage.workshops.values():
            ttk.Label(frame, text=f"{ws.ws_id} | {ws.title} | {len(ws.attendee_ids)}/{ws.capacity}").pack(anchor="w")
        ttk.Button(frame, text="Upgrade attendee ticket", command=self.upgrade_attendee_ticket).pack(pady=6)
        ttk.Button(frame, text="Close", command=self.destroy).pack(pady=6)

    def upgrade_attendee_ticket(self):
        aid = simpledialog.askstring("Upgrade Attendee", "Enter attendee email:")
        att = storage.storage.find_attendee_by_email(aid) if aid else None
        if not att:
            messagebox.showerror("Upgrade", "Attendee not found.")
            return
        if not att.tickets:
            messagebox.showerror("Upgrade", "Attendee has no tickets.")
            return
        tid = att.tickets[0]
        ex_id = simpledialog.askstring("Upgrade Attendee", f"Enter exhibition id to add: {list(storage.storage.exhibitions.keys())}")
        if not ex_id:
            return
        ok = storage.storage.upgrade_ticket(tid, ex_id, extra_price=40.0)
        if ok:
            messagebox.showinfo("Upgrade", "Ticket upgraded by admin.")
        else:
            messagebox.showerror("Upgrade", "Upgrade failed.")
