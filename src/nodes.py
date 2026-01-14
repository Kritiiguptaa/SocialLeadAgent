from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import AgentState
from src.rag import query_knowledge_base
from src.tools import mock_lead_capture
import os

llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)

def intent_classifier(state: AgentState):
    """Step 1: Determine what the user wants."""
    last_user_message = state['messages'][-1]
    
    prompt = f"""
    Classify the user message into exactly one category:
    - "greeting" (Hi, Hello)
    - "inquiry" (Price? Features? Details? Guide me? Tell me about?)
    - "high_intent" (I want to buy, Sign me up, Interested in Pro)

    User Message: "{last_user_message}"
    
    CRITICAL INSTRUCTION: 
    - If the user says "guide me" or "tell me about", classify as "inquiry".
    - Only choose "high_intent" if the user explicitly says they want to BUY, SIGN UP, or REGISTER.
    
    Return ONLY the category word (lowercase).
    """
    response = llm.invoke(prompt).content.strip().lower()
    
    if any(x in response for x in ["buy", "purchase", "sign", "high_intent"]):
        intent = "high_intent"
    elif any(x in response for x in ["inquir", "cost", "price", "feature", "guide", "tell"]):
        intent = "inquiry"
    else:
        intent = "greeting"
        
    return {"intent": intent}

def agent_response(state: AgentState):
    """Step 2a: Answer questions or greet (With JSON Fix)."""
    intent = state['intent']
    last_message = state['messages'][-1]
    
    response_text = ""

    if intent == "inquiry":
        context = query_knowledge_base(last_message)
        prompt = f"Answer using ONLY this context:\n{context}\n\nQuestion: {last_message}"
        response = llm.invoke(prompt)
        
        content = response.content
        if isinstance(content, list):
            response_text = content[0].get("text", "")
        else:
            response_text = str(content)
        
    elif intent == "greeting":
        prompt = f"""
        You are the friendly AI assistant for AutoStream.
        The user just said: "{last_message}"
        Reply with a warm, short greeting under 2 sentences.
        """
        response = llm.invoke(prompt)
        
        content = response.content
        if isinstance(content, list):
            response_text = content[0].get("text", "")
        else:
            response_text = str(content)

    else:
        response_text = "Could you rephrase that? I'm here to help with AutoStream pricing and features."

    return {"messages": [response_text]}

def lead_collector(state: AgentState):
    """Step 2b: Loop to collect Name -> Email -> Platform."""
    last_input = state['messages'][-1]
    
   
    if any(word in last_input.lower() for word in ["cancel", "stop", "no", "wait", "quit", "wrong"]):
         return {
             "step": None, 
             "user_name": None, "user_email": None, "platform": None, 
             "messages": ["Okay, I've cancelled the sign-up. What would you like to know instead?"]
         }

    name = state.get("user_name")
    email = state.get("user_email")
    platform = state.get("platform")
    current_step = state.get("step")

    if current_step == "ask_name": name = last_input
    elif current_step == "ask_email": email = last_input
    elif current_step == "ask_platform": platform = last_input

    if not name:
        return {"step": "ask_name", "messages": ["Great! To get started, what is your full name?"]}
    if not email:
        return {"user_name": name, "step": "ask_email", "messages": [f"Thanks {name}. What is your email?"]}
    if not platform:
        return {"user_email": email, "step": "ask_platform", "messages": ["Got it. Which platform do you use (e.g. YouTube)?"]}

    msg = mock_lead_capture(name, email, platform)
    
    return {
        "platform": platform, 
        "step": None, 
        "messages": [f"Done! {msg} We'll be in touch."]
    }