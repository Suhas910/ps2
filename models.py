from dataclasses import dataclass, field
from typing import List, Tuple
from datetime import datetime

@dataclass
class Order:
    order_id: str
    timestamp: datetime
    location: Tuple[int, int]
    prep_time: int
    priority: str
    sla_minutes: int
    status: str = "PENDING"  # PENDING, ASSIGNED, IN_TRANSIT, DELIVERED
    
    # Using slots for memory/speed optimization
    __slots__ = ['order_id', 'timestamp', 'location', 'prep_time', 'priority', 
                 'sla_minutes', 'status']

@dataclass
class Agent:
    agent_id: str
    pos: Tuple[int, int]
    rating: float
    active_orders: List[str] = field(default_factory=list)
    cumulative_assignments: int = 0
    available_at: float = 0.0  # Simulation time when they become free
    
    __slots__ = ['agent_id', 'pos', 'rating', 'active_orders', 
                 'cumulative_assignments', 'available_at']