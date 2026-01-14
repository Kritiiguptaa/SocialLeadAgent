# AutoStream AI Agent

Hi there! This is the AI Agent I built for the ServiceHive ML Internship assignment. It's designed to act as a first-line support and lead generation bot for "AutoStream," a fictional video editing SaaS.

The bot can answer questions about pricing and features using RAG (Retrieval-Augmented Generation) and detecting when a user is ready to buy—automatically switching gears to collect their lead information.

---

## How to Run It Locally

Getting this running on your machine is pretty straightforward. You'll need Python installed.

### 1. Clone the repo
```bash
git clone <your-repo-url-here>
cd SocialLeadAgent
```
### 2. Set up the environment
```bash
python -m venv venv
# Windows
venv\Scripts\Activate.bat
#Mac
source venv/bin/activate
```
### 3.Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Configure API Keys
Create a .env file in the root directory and add your Google Gemini API key:
GOOGLE_API_KEY=your_actual_api_key_here
### 5. Run the app
```bash
streamlit run app.py
```
---

## Architecture Explanation
### Why LangGraph?
I chose LangGraph over AutoGen for this project because the use case (Lead Generation) requires a deterministic and cyclical flow.

While AutoGen is excellent for open-ended multi-agent collaboration, business support bots need strict guardrails. I needed to ensure that once a user expresses "High Intent," the bot strictly transitions into a data collection loop and doesn't exit until it has the necessary details (Name, Email, Platform). LangGraph's state machine architecture allowed me to define these explicit edges and transitions while still leveraging the LLM's flexibility for natural conversation.

---

## State Management
The agent's memory is managed via a central typed dictionary called AgentState. This state object persists through every step of the graph.

Conversation History: Maintains a running log of messages for context.

Data Slots: Specific fields (user_name, user_email, platform) track the lead's information.

Persistence Strategy: The state is updated incrementally. For example, when the bot asks for an email, it simultaneously saves the name provided in the previous turn. This ensures data integrity even if the conversation flow becomes complex.

---

## WhatsApp Deployment Strategy
To deploy this agent from a local environment to a live WhatsApp number, I would use the WhatsApp Business Cloud API via Meta.

Implementation Plan:

Webhook Setup: I would deploy a FastAPI or Flask endpoint on a cloud server (e.g., AWS EC2 or Render). This endpoint acts as a webhook that receives POST requests from Meta whenever a user sends a message to the business number.

User Identification: Unlike web apps that use session cookies, WhatsApp uses phone numbers as unique identifiers. I would use the user's phone number to retrieve their specific AgentState from a persistent database like Redis or PostgreSQL. This ensures conversation continuity across different sessions.

Processing: The incoming message text is extracted from the JSON payload and passed into the LangGraph app.invoke() function.

Response: Once the agent generates a text response, the system sends a POST request back to Meta's messages endpoint to deliver the reply to the user's WhatsApp thread.

Security: I would implement X-Hub-Signature verification to validate that incoming webhooks are legitimately from Meta.