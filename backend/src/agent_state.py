"""
Agent State Management
Track agent decisions and state transitions
"""

import json
import logging
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentState(Enum):
    IDLE = "idle"
    SEARCHING = "searching"
    MATCHING = "matching"
    RANKING = "ranking"
    COMPLETE = "complete"
    ERROR = "error"


class AgentStateManager:
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.current_state = AgentState.IDLE
        self.history = []
        self.decisions = []
        self.context = {}
        
        logger.info(f"Agent {agent_id} initialized in state {self.current_state.value}")
    
    def transition(self, new_state: AgentState, reason: str = ""):
        """Transition to new state"""
        
        transition = {
            "from": self.current_state.value,
            "to": new_state.value,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        self.history.append(transition)
        self.current_state = new_state
        
        logger.info(f"Agent {self.agent_id}: {self.current_state.value} ({reason})")
    
    def record_decision(self, decision_type: str, data: dict):
        """Record a decision made by agent"""
        
        decision = {
            "type": decision_type,
            "state": self.current_state.value,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.decisions.append(decision)
        logger.info(f"Decision recorded: {decision_type}")
    
    def set_context(self, key: str, value):
        """Set agent context"""
        self.context[key] = value
    
    def get_context(self, key: str):
        """Get agent context"""
        return self.context.get(key)
    
    def get_state_history(self) -> list:
        """Get state transition history"""
        return self.history
    
    def get_decisions(self) -> list:
        """Get all decisions"""
        return self.decisions
    
    def export_state(self, filepath: str):
        """Export agent state"""
        state_export = {
            "agent_id": self.agent_id,
            "current_state": self.current_state.value,
            "history": self.history,
            "decisions": self.decisions,
            "context": self.context
        }
        
        with open(filepath, 'w') as f:
            json.dump(state_export, f, indent=2)
        
        logger.info(f"Agent state exported to {filepath}")