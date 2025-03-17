import unittest
from supermarket_checkout_line_simulation import run_simulation

class TestSupermarketCheckout(unittest.TestCase):
    """Unit tests for the supermarket checkout simulation."""

    def test_hello_world(self):
        """Basic test to ensure the test framework runs."""
        self.assertEqual(1, 1)

    def test_run_simulation(self):
        """Test if the simulation returns all expected statistical keys with valid values."""
        result = run_simulation(1.0, 1.0, 480)  # 1 customer/min arrival, 1 customer/min service, 1 hour
        expected_keys = ['avg_waiting_time', 'cashier_utilization', 'max_queue_length', 'avg_queue_length', 'total_customers']
        
        # Check all expected keys exist
        for key in expected_keys:
            self.assertIn(key, result)

        # Validate values are within reasonable ranges
        self.assertGreaterEqual(result['avg_waiting_time'], 0)
        self.assertGreaterEqual(result['cashier_utilization'], 0)
        self.assertLessEqual(result['cashier_utilization'], 1)
        self.assertGreaterEqual(result['max_queue_length'], 0)
        self.assertGreaterEqual(result['avg_queue_length'], 0)
        self.assertGreaterEqual(result['total_customers'], 0)

    def test_no_customers(self):
        """Test behavior when no customers arrive (arrival rate = 0)."""
        result = run_simulation(0, 1.0, 480)  # No arrivals
        
        # Expecting zero values across all statistics
        self.assertEqual(result['total_customers'], 0)
        self.assertEqual(result['avg_waiting_time'], 0)
        self.assertEqual(result['cashier_utilization'], 0)
        self.assertEqual(result['max_queue_length'], 0)
        self.assertEqual(result['avg_queue_length'], 0)

    def test_high_arrival_rate(self):
        """Test scenario where arrival rate is much higher than service rate."""
        result = run_simulation(5.0, 1.0, 480)  # More customers than the cashier can handle

        # Expect longer wait times and longer queues
        self.assertGreater(result['avg_waiting_time'], 0)
        self.assertGreater(result['max_queue_length'], 1)

    def test_zero_service_rate(self):
        """Test behavior when service rate is extremely low (almost zero, cashier barely serves customers)."""
        result = run_simulation(1.0, 1e-3, 480)  # Customers arrive, but cashier is extremely slow
        
        # Queue should build up significantly since service is very slow
        self.assertGreater(result['max_queue_length'], 10, "Queue should be long due to slow service")
        
        # Cashier should be busy almost 100% of the time (serving very slowly)
        self.assertGreater(result['cashier_utilization'], 0.9, "Cashier should be fully utilized serving slowly")
        
        # Few customers should be processed
        self.assertLess(result['total_customers'], 5, "Few customers should be processed due to slow service")

if __name__ == '__main__':
    unittest.main(exit=False)  # Prevents the script from stopping

