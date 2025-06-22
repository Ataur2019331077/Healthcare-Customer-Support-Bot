# 🏥 Healthcare Chatbot System — LangGraph + Gemini + FastAPI
A modular and intelligent healthcare chatbot system powered by **LangGraph, Google Gemini 2.0 Flash LLM, and FastAPI**. This chatbot automatically **classifies and routes** user messages into predefined medical domains (e.g., `appointments, billing, reports`), interacts with backend APIs, and supports emergency escalation — all using a stateful LangGraph architecture.

## ✨ Key Capabilities
- **🧠 Message Classification via Gemini:**

    Automatically identifies the category of a user's message (e.g., billing, appointment, medical report, etc.)

- **🔁 Message Routing & Flow Control:**

    Directed to the correct agent using LangGraph's StateGraph based on classification.

- **🌐 Backend Integration:**

    Calls FastAPI endpoints for real-time responses.

- **🚨 Emergency Detection:**

    Escalates to medical team and sends appropriate alerts.

- **🧾 Extensible Agent Design:**

    Easily extendable to more domains or APIs.

## 🧰 Tech Stack
| Component           | Description                                        |
|---------------------|----------------------------------------------------|
| 🧠 LangGraph         | State-driven message routing and execution         |
| 🤖 Gemini 2.0 Flash  | Google’s LLM for classification & generation       |
| 🧪 LangChain         | LLM interface & structured output wrappers         |
| ⚙️ FastAPI           | REST API backend (mocked)                          |
| 🧾 Pydantic          | Data validation and structured modeling            |

---

## 📁 Project Structure
```
langgraph-medical-chatbot/
├── main.py              # Core chatbot engine using LangGraph
├── app.py               # FastAPI backend (mock endpoints)
├── requirements.txt     # Python dependencies
├── README.md            # Documentation
```


---

## 🧠 How It Works

### 🧾 1. Message Input
- User sends a message (e.g., "I want to book an appointment in cardiology").

### 🧠 2. Classification
- Gemini LLM classifies the message into one of:
  - `billing`, `appointment`, `medical report`, `complaint`, `procedure`, or fallback to `emergency`.

### 🔁 3. Routing via LangGraph
- LangGraph dynamically routes the message based on its type to the relevant agent:
  - `appointment_agent`, `billing_agent`, etc.

### ⚙️ 4. Agent Processing
- Each agent interacts with the user or queries FastAPI endpoints like:
  - `/appointments/{department}`
  - `/billing/{billing_id}`
  - `/medical_report/{report_id}`

### 🚨 5. Emergency Flow
- When unclassified or critical, messages are escalated to `emergency_agent`, which:
  - Notifies the medical team.
  - Sends a user-friendly response.

---

## 🚀 Getting Started

### 🔧 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 🔑 2. Set Gemini API Key

```
#macos
export GOOGLE_API_KEY="your_api_key_here"

#windows
set GOOGLE_API_KEY="your_api_key_here"
```

### ▶️ 3. Run the Chatbot and Backend
```
# Run LangGraph-based chatbot loop
python main.py

# Run mock FastAPI backend
uvicorn app:app --reload
```

## 💬 Sample Interaction
```
Message: Can I see the doctor list for Oncology?
Assistant: {'appointments': [{'_id': '682f71c5...', 'department_name': 'Oncology', 'doctors': ['Dr. Sarah Bennett', 'Dr. James Lee'], 'available_days': ['Monday', 'Tuesday', ...]}]}
```
  ✅ In your frontend, you can parse and display this data in a structured UI.

## 🔌 Backend Endpoints
Ensure that `FastAPI` backend is available at `http://localhost:8000`, supporting:

| Endpoint                      | Purpose                            |
|------------------------------|------------------------------------|
| `/billing/{billing_id}`      | Fetch billing details              |
| `/appointments/{department}` | List doctors & slots in department |
| `/medical_report/{report_id}`| Retrieve test results/report       |


## 🧪 Testing Tips
- Test different categories by varying user messages.

- Try messages like:

  - “Where is my billing ID 12234?”

  - “Schedule me for surgery next week”

  - “I need a copy of my blood test result”

- Try an ambiguous or urgent message to test emergency routing:

  - “Help! I’m feeling pain in my chest right now!”

## 🧱 Architecture Overview
```
graph TD
    A[User Message] --> B[Gemini Classification]
    B --> C[LangGraph Router]
    C -->|billing| D[Billing Agent]
    C -->|appointment| E[Appointment Agent]
    C -->|medical report| F[Medical Report Agent]
    C -->|complaint| G[Complaint Agent]
    C -->|procedure| H[Procedure Agent]
    C -->|fallback| I[Emergency Agent]
    D --> J[FastAPI GET /billing]
    E --> K[FastAPI GET /appointments]
    F --> L[FastAPI GET /medical_report]
```
## 🧩 Extending This Project
Want to scale it?

- ✅ Add new categories in MessageClassifier and router().

- ✅ Add more agents and backend endpoints.

- ✅ Add memory or context to LangGraph nodes.

- ✅ Integrate with a database or real hospital systems.

## 📄 License
This project is under [MIT License](./LICENSE.md)