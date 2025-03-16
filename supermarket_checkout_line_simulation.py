"""
Supermarket Checkout Line Simulation
-------------------------------------
This program simulates a single checkout line in a supermarket using the SimPy
library. The simulation models customer arrivals, queue lengths, waiting times,
and cashier utilization.

Key Features:
- Customers arrive at an exponential rate.
- A single cashier serves customers one at a time.
- The system tracks and records various statistics.
- Multiple simulations can be run to analyze different arrival rates.
- Results are visualized and saved in "simulation_results.png".

Modules Used:
- simpy: For discrete-event simulation.
- random: To generate random customer arrivals and service times.
- statistics: To calculate averages and distributions.
- matplotlib & pandas: For visualization and tabular representation.
"""

import simpy
import random
import numpy as np
import statistics
import matplotlib.pyplot as plt
import pandas as pd
from collections import deque

class SupermarketCheckout:
    """
    Simulates a single checkout process in a supermarket.
    
    Attributes:
    - env: SimPy environment
    - arrival_rate: Customer arrival rate (customers per minute)
    - service_rate: Service rate (customers per minute)
    - simulation_duration: Total duration of the simulation (minutes)
    - cashier: SimPy resource representing the cashier
    - waiting_times: List to track individual customer wait times
    - queue_lengths: Stores queue length at different timestamps
    - queue_length_times: Corresponding timestamps for queue lengths
    - cashier_busy_time: Accumulates total cashier usage time
    - max_queue_length: Stores the longest observed queue length
    """

    def __init__(self, env, arrival_rate, service_rate, simulation_duration):
        self.env = env
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.simulation_duration = simulation_duration
        self.cashier = simpy.Resource(env, capacity=1)  # Single cashier
        
        # Tracking statistics
        self.waiting_times = []
        self.queue_lengths = deque()
        self.queue_length_times = deque()
        self.cashier_busy_time = 0
        self.max_queue_length = 0
        
        # Start customer arrivals and queue monitoring
        self.env.process(self.customer_arrivals())
        self.env.process(self.monitor_queue())
    
    def customer_arrivals(self):
        """Generates customers at exponentially distributed intervals."""
        while self.env.now <= self.simulation_duration:
            if self.arrival_rate > 0:
                yield self.env.timeout(random.expovariate(self.arrival_rate))
                self.env.process(self.customer_service())
            else:
                break  # Prevents division by zero error
    
    def customer_service(self):
        """Handles the checkout process for a single customer."""
        arrival_time = self.env.now  # Capture arrival time
        with self.cashier.request() as request:
            yield request  # Wait for cashier availability
            wait_time = self.env.now - arrival_time  # Compute wait time
            self.waiting_times.append(wait_time)
            service_time = random.expovariate(self.service_rate)  # Randomized service time
            self.cashier_busy_time += service_time
            yield self.env.timeout(service_time)  # Simulate service
    
    def monitor_queue(self):
        """Records queue length at regular intervals to track congestion."""
        while self.env.now <= self.simulation_duration:
            self.queue_lengths.append(len(self.cashier.queue))
            self.queue_length_times.append(self.env.now)
            self.max_queue_length = max(self.max_queue_length, len(self.cashier.queue))
            yield self.env.timeout(0.1)  # Monitor every 0.1 minute
    
    def get_statistics(self):
        """Returns key performance metrics of the checkout simulation."""
        return {
            'avg_waiting_time': statistics.mean(self.waiting_times) if self.waiting_times else 0,
            'cashier_utilization': self.cashier_busy_time / max(self.env.now, 1),
            'max_queue_length': self.max_queue_length,
            'avg_queue_length': statistics.mean(self.queue_lengths) if self.queue_lengths else 0,
            'total_customers': len(self.waiting_times)
        }

def run_simulation(arrival_rate, service_rate, simulation_duration):
    """Runs a single simulation instance and returns statistics."""
    env = simpy.Environment()
    checkout = SupermarketCheckout(env, arrival_rate, service_rate, simulation_duration)
    env.run(until=simulation_duration)
    return checkout.get_statistics()

def run_multiple_simulations(arrival_rates, service_rate, simulation_duration, num_runs=5):
    """Runs multiple simulations with different arrival rates and aggregates results."""
    results = []
    for arrival_rate in arrival_rates:
        run_stats = [run_simulation(arrival_rate, service_rate, simulation_duration) for _ in range(num_runs)]
        results.append({
            'arrival_rate': arrival_rate,
            'service_rate': service_rate,
            'avg_waiting_time': statistics.mean(stat['avg_waiting_time'] for stat in run_stats),
            'cashier_utilization': statistics.mean(stat['cashier_utilization'] for stat in run_stats),
            'max_queue_length': statistics.mean(stat['max_queue_length'] for stat in run_stats),
            'avg_queue_length': statistics.mean(stat['avg_queue_length'] for stat in run_stats),
            'total_customers': statistics.mean(stat['total_customers'] for stat in run_stats)
        })
    return results

def plot_results(results):
    """Generates visualizations for simulation results and saves to file."""
    df = pd.DataFrame(results)
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    
    plots = [
        ('avg_waiting_time', 'Average Waiting Time (min)', 'blue'),
        ('cashier_utilization', 'Cashier Utilization (%)', 'green'),
        ('max_queue_length', 'Maximum Queue Length', 'red'),
        ('avg_queue_length', 'Average Queue Length', 'purple')
    ]
    
    for ax, (key, ylabel, color) in zip(axs.flat, plots):
        ax.plot(df['arrival_rate'], df[key], 'o-', color=color)
        ax.set_xlabel('Arrival Rate (customers/min)')
        ax.set_ylabel(ylabel)
        ax.set_title(f'{ylabel} vs Arrival Rate')
        ax.grid(True)
    
    plt.tight_layout()
    plt.savefig('simulation_results.png')
    plt.close()
    return fig

# Simulation Configuration
SERVICE_RATE = 1.0  # Cashier serves 1 customer per minute
SIMULATION_DURATION = 480  # Simulate an 8-hour workday (480 minutes)
ARRIVAL_RATES = [0.5, 0.7, 0.9, 1.0, 1.1, 1.3, 1.5]  # Varying customer arrival rates

# Execute Simulations
results = run_multiple_simulations(ARRIVAL_RATES, SERVICE_RATE, SIMULATION_DURATION, num_runs=5)

# Display Results as a Table
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# Generate Plots
plot_results(results)
