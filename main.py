import time
from data_loader import load_orders, load_agents, load_constraints
from graph_engine import GraphEngine
from dispatcher import Dispatcher
from datetime import timedelta
import json;

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
                order.delivery_time = completion_time  # Record the time!
                delivered_orders.append(order)
                actual_duration = (completion_time - order.timestamp).total_seconds() / 60
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
        # Batch assignment: try to assign all current pending orders once per tick,
        # and requeue unassigned orders for later when agents free up.
        if dispatcher.pending_queue:
            max_active = int(constraints['max_active_orders_per_agent'])
            pending_requeue = []
            assigned_any = False

            while dispatcher.pending_queue:
                _, _, current_order = dispatcher.pop_next_order()
                best_agent = None
                best_score = float('inf')
                best_travel_time = 0

                for agent in agents:
                    if len(agent.active_orders) < max_active:
                        travel_time = graph.get_dist(agent.pos, current_order.location)
                        score = dispatcher.score_agent(agent, current_order, travel_time)

                        if score < best_score:
                            best_score = score
                            best_agent = agent
                            best_travel_time = travel_time

                if best_agent:
                    assigned_any = True
                    best_agent.active_orders.append(current_order.order_id)
                    best_agent.cumulative_assignments += 1

                    # Calculate completion time: Current + Prep + Travel
                    finish_time = current_time + timedelta(minutes=(current_order.prep_time + best_travel_time))
                    active_assignments.append((finish_time, best_agent, current_order))

                    # Agent's new position will be the delivery location
                    best_agent.pos = current_order.location
                    current_order.status = "ASSIGNED"
                else:
                    pending_requeue.append((current_order.priority, current_order.timestamp, current_order))

            for _, _, order_obj in pending_requeue:
                dispatcher.add_to_queue(order_obj)

            # Wait-and-see: if no assignment could be made this minute, let time advance
            # so agents can finish current deliveries before reattempting.
            if not assigned_any and active_assignments:
                pass

        current_time += timedelta(minutes=1)

    print(f"\nSimulation Finished. Total Orders Delivered: {len(delivered_orders)}")

    # Add this at the very end of run_simulation()
    total_orders = len(delivered_orders)
    # Issue 12: Average Delivery Time
    if total_orders > 0:
        avg_time = sum((o.delivery_time - o.timestamp).total_seconds() / 60 for o in delivered_orders) / total_orders
    else:
        avg_time = 0.0
    # Issue 14: Fairness (Standard Deviation of assignments)
    assignments = [a.cumulative_assignments for a in agents]
    if len(agents) > 0:
        mean_ass = sum(assignments) / len(agents)
        variance = sum((x - mean_ass) ** 2 for x in assignments) / len(agents)
    else:
        variance = 0.0

    print(f"\n--- FINAL REPORT ---")
    print(f"Avg Delivery Time: {avg_time:.2f} mins")
    print(f"Workload Variance: {variance:.2f}")

    # After the loop finishes
    metrics = {
        "total_orders": len(delivered_orders),
        "avg_delivery_time_mins": sum((o.delivery_time - o.timestamp).total_seconds() / 60 for o in delivered_orders) / len(delivered_orders) if delivered_orders else 0,
        "sla_compliance_rate": (len([o for o in delivered_orders if (o.delivery_time - o.timestamp).total_seconds() / 60 <= o.sla_minutes]) / len(delivered_orders)) * 100 if delivered_orders else 0,
        "workload_variance": variance # Use the variance calculation from your current report
    }

    with open('metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)


if __name__ == "__main__":
    run_simulation()