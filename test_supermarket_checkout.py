import unittest
from supermarket_checkout_line_simulation import run_simulation

class TestSupermarketCheckout(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual(1, 1)

    def test_run_simulation(self):
        result = run_simulation(1.0, 1.0, 60)
        self.assertIn('avg_waiting_time', result)
        self.assertIn('cashier_utilization', result)
        self.assertIn('max_queue_length', result)
        self.assertIn('avg_queue_length', result)
        self.assertIn('total_customers', result)

if __name__ == '__main__':
    unittest.main()