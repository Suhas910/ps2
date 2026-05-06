import time
from data_loader import load_orders, load_agents, load_constraints
from graph_engine import GraphEngine
from dispatcher import Dispatcher
from datetime import timedelta

def run_simulation():
    # 1. SETUP
    print("Initializing Engine...")
    graph = GraphEngine('data/raw/environment_edges.csv')
    constraints = load_constraints('data/raw/constraints.csv')
    all_orders = load_orders('data/raw/orders.csv')
    agents = load_agents('data/raw/agents.csv')
    dispatcher = Dispatcher(constraints)
    
    all_orders.sort(key=lambda x: x.timestamp)
    current_time = all_orders[0].timestamp
    # End simulation when all orders are DELIVERED
    delivered_orders = []
    active_assignments = [] # List to track (completion_time, agent, order)

    print(f"Simulation started...")

    # 2. MAIN LOOP
    # Continue as long as there are orders to process or deliver
    while all_orders or dispatcher.pending_queue or active_assignments:
        
        # A. COMPLETE DELIVERIES (Issue 10)
        # Check if any agent has reached their destination at this current_time
        still_traveling = []
        for completion_time, agent, order in active_assignments:
            if current_time >= completion_time:
                agent.active_orders.remove(order.order_id)
                order.status = "DELIVERED"
                delivered_orders.append(order)
                
                # Check SLA (Issue 13)
                actual_duration = (current_time - order.timestamp).total_seconds() / 60
                if actual_duration > order.sla_minutes:
                    print(f"⚠️ SLA VIOLATION: {order.order_id} delivered in {actual_duration}m")
                else:
                    print(f"✅ SUCCESS: {order.order_id} delivered by {agent.agent_id}")
            else:
                still_traveling.append((completion_time, agent, order))
        active_assignments = still_traveling

        # B. INGEST NEW ORDERS
        while all_orders and all_orders[0].timestamp <= current_time:
            new_order = all_orders.pop(0)
            dispatcher.add_to_queue(new_order)

        # C. DISPATCH (Issue 11 - Handling Queueing)
        # Try to assign as many pending orders as possible
        if dispatcher.pending_queue:
            # We use a copy of the queue to iterate safely
            for i in range(len(dispatcher.pending_queue)):
                _, _, current_order = dispatcher.pending_queue[0]
                
                best_agent = None
                best_score = float('inf')
                best_travel_time = 0

                for agent in agents:
                    if len(agent.active_orders) < int(constraints['max_active_orders_per_agent']):
                        # Optimization: Distance lookup is O(1)
                        travel_time = graph.get_dist(agent.pos, current_order.location)
                        score = dispatcher.score_agent(agent, current_order, travel_time, 0)
                        
                        if score < best_score:
                            best_score = score
                            best_agent = agent
                            best_travel_time = travel_time

                if best_agent:
                    dispatcher.pending_queue.pop(0)
                    best_agent.active_orders.append(current_order.order_id)
                    best_agent.cumulative_assignments += 1
                    
                    # Calculate completion time: Current + Prep + Travel
                    finish_time = current_time + timedelta(minutes=(current_order.prep_time + best_travel_time))
                    active_assignments.append((finish_time, best_agent, current_order))
                    
                    # Agent's new position will be the delivery location
                    best_agent.pos = current_order.location
                    current_order.status = "ASSIGNED"
                else:
                    # No agents available for the top priority order, stop trying for this minute
                    break

        current_time += timedelta(minutes=1)

    print(f"\nSimulation Finished. Total Orders Delivered: {len(delivered_orders)}")

if __name__ == "__main__":
    run_simulation()