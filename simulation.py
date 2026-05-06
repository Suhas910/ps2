import heapq
import json
from datetime import timedelta
from data_loader import load_orders, load_agents, load_constraints
from graph_engine import GraphEngine
from dispatcher import Dispatcher


def run_simulation(
    edges_path='data/raw/environment_edges.csv',
    constraints_path='data/raw/constraints.csv',
    orders_path='data/raw/orders.csv',
    agents_path='data/raw/agents.csv',
    export_metrics=True,
    verbose=True,
):
    graph = GraphEngine(edges_path)
    constraints = load_constraints(constraints_path)
    all_orders = load_orders(orders_path)
    agents = load_agents(agents_path)
    dispatcher = Dispatcher(constraints)

    all_orders.sort(key=lambda x: x.timestamp)
    current_time = all_orders[0].timestamp if all_orders else None
    delivered_orders = []
    active_assignments = []

    if verbose:
        print('Initializing Engine...')
        print('Simulation started...')

    while all_orders or dispatcher.pending_queue or active_assignments:
        still_traveling = []
        for completion_time, agent, order in active_assignments:
            if current_time >= completion_time:
                agent.active_orders.remove(order.order_id)
                order.status = 'DELIVERED'
                order.delivery_time = completion_time
                delivered_orders.append(order)
                actual_duration = (completion_time - order.timestamp).total_seconds() / 60
                if actual_duration > order.sla_minutes and verbose:
                    print(f'⚠️ SLA VIOLATION: {order.order_id} delivered in {actual_duration}m')
                elif verbose:
                    print(f'✅ SUCCESS: {order.order_id} delivered by {agent.agent_id}')
            else:
                still_traveling.append((completion_time, agent, order))
        active_assignments = still_traveling

        while all_orders and all_orders[0].timestamp <= current_time:
            new_order = all_orders.pop(0)
            dispatcher.add_to_queue(new_order)

        if dispatcher.pending_queue:
            p_val, ts, current_order = heapq.heappop(dispatcher.pending_queue)
            best_agent = None
            best_score = float('inf')
            best_travel = 0

            for agent in agents:
                if len(agent.active_orders) < int(constraints['max_active_orders_per_agent']):
                    travel_time = graph.get_dist(agent.pos, current_order.location)
                    if travel_time == float('inf'):
                        continue
                    score = dispatcher.score_agent(agent, current_order, travel_time)
                    if score < best_score:
                        best_score = score
                        best_agent = agent
                        best_travel = travel_time

            if best_agent:
                best_agent.active_orders.append(current_order.order_id)
                best_agent.cumulative_assignments += 1
                current_order.assigned_agent = best_agent.agent_id
                finish_time = current_time + timedelta(minutes=(current_order.prep_time + best_travel))
                active_assignments.append((finish_time, best_agent, current_order))
                best_agent.pos = current_order.location
                current_order.status = 'ASSIGNED'
            else:
                heapq.heappush(dispatcher.pending_queue, (p_val, ts, current_order))

        if current_time is None:
            break
        current_time += timedelta(minutes=1)

    total_orders = len(delivered_orders)
    if total_orders > 0:
        avg_time = sum((o.delivery_time - o.timestamp).total_seconds() / 60 for o in delivered_orders) / total_orders
    else:
        avg_time = 0.0
    assignments = [a.cumulative_assignments for a in agents]
    if len(agents) > 0:
        mean_ass = sum(assignments) / len(agents)
        variance = sum((x - mean_ass) ** 2 for x in assignments) / len(agents)
    else:
        variance = 0.0

    if verbose:
        print('\n--- FINAL REPORT ---')
        print(f'Avg Delivery Time: {avg_time:.2f} mins')
        print(f'Workload Variance: {variance:.2f}')

    report = {
        'overall': {
            'avg_time': avg_time,
            'variance': variance,
            'total_delivered': total_orders,
        },
        'agent_load': {a.agent_id: a.cumulative_assignments for a in agents},
    }

    if export_metrics:
        export_metrics_file(delivered_orders, agents, avg_time, variance)

    return {
        'summary': report['overall'],
        'agents': [
            {
                'agent_id': a.agent_id,
                'rating': a.rating,
                'current_position': a.pos,
                'assignments': a.cumulative_assignments,
                'active_orders': a.active_orders,
            }
            for a in agents
        ],
        'orders': [
            {
                'order_id': o.order_id,
                'priority': o.priority,
                'timestamp': o.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'location': o.location,
                'sla_minutes': o.sla_minutes,
                'prep_time': o.prep_time,
                'status': o.status,
                'delivery_time': o.delivery_time.strftime('%Y-%m-%d %H:%M:%S') if o.delivery_time else None,
                'assigned_agent': o.assigned_agent,
            }
            for o in delivered_orders
        ],
    }


def export_metrics_file(delivered_orders, agents, avg_time, variance):
    report = {
        'overall': {
            'avg_time': avg_time,
            'variance': variance,
        },
        'agent_load': {a.agent_id: a.cumulative_assignments for a in agents},
    }
    with open('metrics.json', 'w') as f:
        json.dump(report, f, indent=4)
