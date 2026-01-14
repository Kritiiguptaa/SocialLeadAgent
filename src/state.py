from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    messages: List[str]      
    intent: str               # "greeting", "inquiry", or "high_intent"
    user_name: Optional[str]  
    user_email: Optional[str] 
    platform: Optional[str]   
    step: str                 