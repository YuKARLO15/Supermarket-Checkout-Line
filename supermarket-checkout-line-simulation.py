import simpy
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from collections import deque

class SupermarketCheckout:
    def __init__(self, env, arrival_rate, service_rate, simulation_duration):
        """
        Initialize the supermarket checkout simulation.
        
        Parameters:
        - env: SimPy environment
        - arrival_rate: Average number of customers arriving per minute
        - service_rate: Average number of customers that can be served per minute
        - simulation_duration: Duration of the simulation in minutes
        """
        self.env = env
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.simulation_duration = simulation_duration
        
        # SimPy resources
        self.cashier = simpy.Resource(env, capacity=1)
        
        # Statistics
        self.waiting_times = []
        self.queue_lengths = deque()
        self.queue_length_times = deque()
        self.service_start_times = []
        self.service_times = []
        self.cashier_busy_time = 0
        self.max_queue_length = 0
        
        # Start the simulation
        self.env.process(self.customer_arrivals())
        self.env.process(self.monitor_queue())
    
    def customer_arrivals(self):
        """Generate customer arrivals based on arrival rate."""
        customer_id = 0
        while True:
            # Wait for next customer to arrive (exponential distribution)
            interarrival_time = random.expovariate(self.arrival_rate)
            yield self.env.timeout(interarrival_time)
            
            # Check if we're still within the simulation duration
            if self.env.now > self.simulation_duration:
                break
                
            # Create a new customer
            customer_id += 1
            self.env.process(self.customer_service(customer_id))
    
    def customer_service(self, customer_id):
        """Process a customer through checkout."""
        arrival_time = self.env.now
        
        # Request cashier
        with self.cashier.request() as request:
            # Wait until it's this customer's turn
            yield request
            
            # Calculate waiting time (time from arrival until service begins)
            wait_time = self.env.now - arrival_time
            self.waiting_times.append(wait_time)
            self.service_start_times.append(self.env.now)
            
            # Service time follows an exponential distribution
            service_time = random.expovariate(self.service_rate)
            self.service_times.append(service_time)
            
            # Simulate the checkout process
            self.cashier_busy_time += service_time
            yield self.env.timeout(service_time)
    
    def monitor_queue(self):
        """Monitor queue length over time."""
        while True:
            if self.env.now > self.simulation_duration:
                break
                
            # Record current queue length and time
            current_queue_length = len(self.cashier.queue)
            self.queue_lengths.append(current_queue_length)
            self.queue_length_times.append(self.env.now)
            
            # Update maximum queue length
            self.max_queue_length = max(self.max_queue_length, current_queue_length)
            
            # Check every 0.1 minute
            yield self.env.timeout(0.1)
    
    def get_statistics(self):
        """Calculate and return simulation statistics."""
        avg_waiting_time = np.mean(self.waiting_times) if self.waiting_times else 0
        cashier_utilization = self.cashier_busy_time / max(self.env.now, 1)  # Prevent division by zero
        
        # Calculate time-weighted average queue length
        time_intervals = np.diff(list(self.queue_length_times) + [self.simulation_duration])
        avg_queue_length = np.average(list(self.queue_lengths)[:-1], weights=time_intervals) if self.queue_lengths else 0
        
        return {
            'avg_waiting_time': avg_waiting_time,
            'cashier_utilization': cashier_utilization,
            'max_queue_length': self.max_queue_length,
            'avg_queue_length': avg_queue_length,
            'total_customers': len(self.waiting_times)
        }

def run_simulation(arrival_rate, service_rate, simulation_duration):
    """Run a single simulation with given parameters."""
    # Create environment
    env = simpy.Environment()
    
    # Create and run checkout simulation
    checkout = SupermarketCheckout(env, arrival_rate, service_rate, simulation_duration)
    env.run(until=simulation_duration)
    
    # Return statistics
    return checkout.get_statistics()

def run_multiple_simulations(arrival_rates, service_rate, simulation_duration, num_runs=5):
    """Run multiple simulations with different arrival rates."""
    results = []
    
    for arrival_rate in arrival_rates:
        run_stats = []
        for _ in range(num_runs):
            stats = run_simulation(arrival_rate, service_rate, simulation_duration)
            run_stats.append(stats)
        
        # Calculate average statistics across runs
        avg_stats = {
            'arrival_rate': arrival_rate,
            'service_rate': service_rate,
            'avg_waiting_time': np.mean([stat['avg_waiting_time'] for stat in run_stats]),
            'cashier_utilization': np.mean([stat['cashier_utilization'] for stat in run_stats]),
            'max_queue_length': np.mean([stat['max_queue_length'] for stat in run_stats]),
            'avg_queue_length': np.mean([stat['avg_queue_length'] for stat in run_stats]),
            'total_customers': np.mean([stat['total_customers'] for stat in run_stats])
        }
        results.append(avg_stats)
    
    return results

def plot_results(results):
    """Create plots to visualize simulation results."""
    # Convert results to DataFrame for easier plotting
    df = pd.DataFrame(results)
    
    # Create subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: Average waiting time vs arrival rate
    axs[0, 0].plot(df['arrival_rate'], df['avg_waiting_time'], 'o-', color='blue')
    axs[0, 0].set_xlabel('Arrival Rate (customers/min)')
    axs[0, 0].set_ylabel('Average Waiting Time (min)')
    axs[0, 0].set_title('Average Waiting Time vs Arrival Rate')
    axs[0, 0].grid(True)
    
    # Plot 2: Cashier utilization vs arrival rate
    axs[0, 1].plot(df['arrival_rate'], df['cashier_utilization'] * 100, 'o-', color='green')
    axs[0, 1].set_xlabel('Arrival Rate (customers/min)')
    axs[0, 1].set_ylabel('Cashier Utilization (%)')
    axs[0, 1].set_title('Cashier Utilization vs Arrival Rate')
    axs[0, 1].grid(True)
    
    # Plot 3: Maximum queue length vs arrival rate
    axs[1, 0].plot(df['arrival_rate'], df['max_queue_length'], 'o-', color='red')
    axs[1, 0].set_xlabel('Arrival Rate (customers/min)')
    axs[1, 0].set_ylabel('Maximum Queue Length')
    axs[1, 0].set_title('Maximum Queue Length vs Arrival Rate')
    axs[1, 0].grid(True)
    
    # Plot 4: Average queue length vs arrival rate
    axs[1, 1].plot(df['arrival_rate'], df['avg_queue_length'], 'o-', color='purple')
    axs[1, 1].set_xlabel('Arrival Rate (customers/min)')
    axs[1, 1].set_ylabel('Average Queue Length')
    axs[1, 1].set_title('Average Queue Length vs Arrival Rate')
    axs[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('simulation_results.png')
    plt.close()
    
    return fig

# Main simulation parameters
SERVICE_RATE = 1.0  # Cashier can serve 1 customer per minute on average
SIMULATION_DURATION = 480  # 8-hour day in minutes
ARRIVAL_RATES = [0.5, 0.7, 0.9, 1.0, 1.1, 1.3, 1.5]  # Varying arrival rates

# Run simulations
results = run_multiple_simulations(ARRIVAL_RATES, SERVICE_RATE, SIMULATION_DURATION, num_runs=5)

# Display results as a table
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# Generate plots
plot_results(results)