from ..agents import AGENT_REGISTRY
from ..state import GraphState, Email

def email_categorizer_node(state: GraphState):
    """
    Node that categorizes the current email using the email categorizer agent.
    """
    body = ""
    email = state.get('current_email')
    if not email:
        #raise ValueError("No current email found in state.")
        state['email_category'] = "No email"
        return state
    if isinstance(email, Email):
        body = email.body
    #categorizer_agent = AGENT_REGISTRY.get("email_categorizer")
    result = AGENT_REGISTRY["email_categorizer"].invoke({"email": body})
    state['email_category'] = result['category']
    return state
