import numpy as np
import datetime

def simulate_delivery(throughput_history, backlog_size, target_date):
    """
    Monte Carlo simulation to estimate probability of completing backlog by target_date.
    throughput_history: list of items completed per day (last 30 days)
    backlog_size: number of items remaining
    target_date: date
    """
    if not throughput_history:
        return 0.0
    
    today = datetime.date.today()
    days_remaining = (target_date - today).days
    
    if days_remaining <= 0:
        return 0.0
        
    simulations = 1000
    success_count = 0
    
    # Simple bootstrap
    for _ in range(simulations):
        # Sample throughput for each remaining day
        daily_throughput = np.random.choice(throughput_history, size=days_remaining)
        total_completed = np.sum(daily_throughput)
        if total_completed >= backlog_size:
            success_count += 1
            
    return success_count / simulations
