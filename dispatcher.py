import heapq

class Dispatcher:
    def __init__(self, constraints):
        self.constraints = constraints
        self.pending_queue = []  # Issue 4: Priority Queue
        self.priority_map = {"high": 1, "normal": 2, "low": 3}

    def add_to_queue(self, order):
        # Issue 11: Priority-based sorting
        p_val = self.priority_map.get(order.priority, 2)
        heapq.heappush(self.pending_queue, (p_val, order.timestamp, order))

    def pop_next_order(self):
        return heapq.heappop(self.pending_queue) if self.pending_queue else None

    def score_agent(self, agent, order, travel_time):
        # Issue 7 & 8: Multivariate Scoring Heuristic
        total_trip = order.prep_time + travel_time
        
        # Penalize workload to maintain fairness (Issue 14)
        fairness_penalty = agent.cumulative_assignments * 1.5
        
        # Priority boost (Issue 7)
        p_weight = float(self.constraints.get(f'priority_weight_{order.priority}', 1.0))
        
        # Efficiency Score: Lower is better
        return ((total_trip / agent.rating) + fairness_penalty) / p_weight
