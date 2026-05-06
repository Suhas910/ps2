import heapq

class Dispatcher:
    def __init__(self, constraints):
        self.constraints = constraints
        # main.py expects this attribute
        self.pending_queue = [] 

    def add_to_queue(self, order):
        # Use a heap so the top-priority order is always at index 0.
        # Stores tuples of (priority_value, timestamp, order_object).
        priority_map = {"high": 1, "normal": 2, "low": 3}
        val = priority_map.get(order.priority, 2)
        heapq.heappush(self.pending_queue, (val, order.timestamp, order))

    def pop_next_order(self):
        return heapq.heappop(self.pending_queue) if self.pending_queue else None

    def score_agent(self, agent, order, travel_time):
        # Total estimated time from current moment to delivery
        total_time = order.prep_time + travel_time

        # 1. SLA Risk Modifier: Exponentially punish high risk
        # If the delivery takes up 80% of the SLA, we prioritize it heavily
        sla_usage = total_time / order.sla_minutes
        sla_risk_penalty = (sla_usage ** 3) * 50  # Spikes as it approaches 1.0

        # 2. Fairness Penalty: Gradually increase cost for busy agents
        # This reduces workload variance
        fairness_penalty = agent.cumulative_assignments * 1.2

        # 3. Agent Efficiency: Reward higher ratings
        rating_bonus = agent.rating * 2.0

        # 4. Priority Multiplier: Lower score is better
        p_map = {"high": 1.5, "normal": 1.0, "low": 0.7}
        priority_boost = p_map.get(order.priority, 1.0)

        # Combined Heuristic Score
        return (total_time + sla_risk_penalty + fairness_penalty - rating_bonus) / priority_boost
