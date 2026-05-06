import pandas as pd
from datetime import datetime
from models import Order, Agent

def load_orders(file_path):
    try:
        df = pd.read_csv(file_path)
        orders = []
        for _, row in df.iterrows():
            orders.append(Order(
                order_id=row['order_id'],
                timestamp=datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S'),
                location=(int(row['location_x']), int(row['location_y'])),
                prep_time=int(row['prep_time_minutes']),
                priority=row['priority'].lower(),
                sla_minutes=int(row['sla_minutes'])
            ))
        return orders
    except Exception as e:
        print(f"Error loading orders: {e}")
        return []

def load_agents(file_path):
    try:
        df = pd.read_csv(file_path)
        agents = []
        for _, row in df.iterrows():
            agents.append(Agent(
                agent_id=row['agent_id'],
                pos=(int(row['current_x']), int(row['current_y'])),
                rating=float(row['rating'])
            ))
        return agents
    except Exception as e:
        print(f"Error loading agents: {e}")
        return []

def load_constraints(file_path):
    df = pd.read_csv(file_path)
    # Converts two columns into a dictionary for O(1) access
    return dict(zip(df['constraint'], df['value']))