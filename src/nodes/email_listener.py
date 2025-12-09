from src.state import GraphState
from src.utils.gmail_utils import get_most_recent_email

def email_listener_node(state: GraphState):
    """
    Node that listens for the most recent email and updates the state.
    """
    email = get_most_recent_email()
    state['current_email'] = email
    return state