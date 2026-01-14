import streamlit as st
from src.agent import app
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AutoStream AI")

st.title("AutoStream AI Assistant")
st.markdown("Ask me about pricing, features, or sign up for a plan!")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "messages": [], 
        "intent": "", 
        "user_name": None, 
        "user_email": None, 
        "platform": None, 
        "step": "start"
    }

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message here..."):
    st.chat_message("user").markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    st.session_state.agent_state["messages"].append(prompt)

    with st.spinner("Thinking..."):
        try:
            result = app.invoke(st.session_state.agent_state)
            
            st.session_state.agent_state = result
            
            agent_response = result["messages"][-1]
            
            with st.chat_message("assistant"):
                st.markdown(agent_response)
            
            st.session_state.messages.append({"role": "assistant", "content": agent_response})
            
        except Exception as e:
            st.error(f"An error occurred: {e}")