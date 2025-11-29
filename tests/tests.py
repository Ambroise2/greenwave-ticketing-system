
import unittest
import shutil
import os
from src.storage import storage
from src.logic import create_account, purchase_ticket, reserve_workshop, cancel_reservation

class TestGreenWave(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # make a clean data dir for testing
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        # Use actual storage.data dir (../data). We won't delete in this environment.
        pass

    def test_account_and_purchase_and_reservation(self):
        # create an account
        a = create_account("Auto Tester", "autotest@example.com", "testpass")
        self.assertIn(a.user_id, storage.attendees)
        ticket, payment = purchase_ticket(a.user_id, "Exhibition", selected_ex_ids=["EX1"])
        self.assertIn(ticket.ticket_id, storage.tickets)
        # reserve a workshop
        ws_id = None
        for w in storage.workshops.values():
            if w.ex_id == "EX1":
                ws_id = w.ws_id
                break
        self.assertIsNotNone(ws_id)
        res = reserve_workshop(a.user_id, ticket.ticket_id, ws_id)
        self.assertIn(res.res_id, storage.reservations)
        cancel_reservation(res.res_id)
        self.assertEqual(storage.reservations[res.res_id].status, "CANCELLED")

if __name__ == "__main__":
    unittest.main()
