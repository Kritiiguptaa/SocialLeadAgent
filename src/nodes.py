from langchain_google_genai import ChatGoogleGenerativeAI
from src.state import AgentState
from src.rag import query_knowledge_base
from src.tools import mock_lead_capture
import os

# llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)

def intent_classifier(state: AgentState):
    last_user_message = state['messages'][-1]
    
    prompt = f"""
    Classify the user message into exactly one category:
    - "greeting" (Hi, Hello)
    - "inquiry" (Price? Features? Details?)
    - "high_intent" (I want to buy, Sign me up, Interested in Pro)

    User Message: "{last_user_message}"
    Return ONLY the category word (lowercase).
    """
    response = llm.invoke(prompt).content.strip().lower()
    
    # Simple normalization to ensure safety
    if any(x in response for x in ["buy", "sign", "purchase", "high_intent"]):
        intent = "high_intent"
    elif any(x in response for x in ["inquir", "cost", "price", "feature", "guide", "tell"]):
        intent = "inquiry"
    else:
        intent = "greeting"
        
    return {"intent": intent}

def agent_response(state: AgentState):
    intent = state['intent']
    last_message = state['messages'][-1]
    
    if intent == "inquiry":
        context = query_knowledge_base(last_message)
        prompt = f"Answer using ONLY this context:\n{context}\n\nQuestion: {last_message}"
        response_text = llm.invoke(prompt).content
        
    elif intent == "greeting":
        prompt = f"""
        You are the friendly AI assistant for AutoStream (a video editing SaaS).
        The user just said: "{last_message}"
        
        Reply with a warm, short greeting. 
        Mention that you can help with pricing, features, or signing up.
        Keep it under 2 sentences.
        """
        response_text = llm.invoke(prompt).content  
        
    else:
        prompt = f"The user said '{last_message}', which is unclear. Politely ask them to rephrase."
        response_text = llm.invoke(prompt).content

    return {"messages": [response_text]}

def lead_collector(state: AgentState):
    """Step 2b: Loop to collect Name -> Email -> Platform."""
    last_input = state['messages'][-1]
    
    name = state.get("user_name")
    email = state.get("user_email")
    platform = state.get("platform")
    current_step = state.get("step")

    if current_step == "ask_name": name = last_input
    elif current_step == "ask_email": email = last_input
    elif current_step == "ask_platform": platform = last_input

   
    if not name:
        return {"step": "ask_name", "messages": ["Great! What is your full name?"]}
    if not email:
        return {"user_name": name, "step": "ask_email", "messages": [f"Thanks {name}. What is your email?"]}
    if not platform:
        return {"user_email": email, "step": "ask_platform", "messages": ["Got it. Which platform do you use (e.g. YouTube)?"]}

    msg = mock_lead_capture(name, email, platform)
    return {
        "platform": platform, 
        "step": "complete", 
        "messages": [f"Done! {msg} We'll be in touch."]
    }