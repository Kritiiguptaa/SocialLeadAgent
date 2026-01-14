import os
from dotenv import load_dotenv
from src.agent import app

# Load environment variables
load_dotenv()

def main():

    state = {
        "messages": [], 
        "intent": "", 
        "user_name": None, 
        "user_email": None, 
        "platform": None,
        "step": "start"
    }

    while True:
        try:
            user_input = input("\nUser: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                break
            
            state["messages"].append(user_input)

            result = app.invoke(state)
            
            state = result

            print(f"Agent: {state['messages'][-1]}")

        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()