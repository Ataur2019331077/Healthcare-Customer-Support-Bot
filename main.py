from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
import requests


import os
from langchain.chat_models import init_chat_model

os.environ["GOOGLE_API_KEY"] = "AIzaSyDcFma_F_a0BT6s-GcoSKcAJtN5eTvoFvo"

llm = init_chat_model("google_genai:gemini-2.0-flash")

class MessageClassifier(BaseModel):
    message_type: Literal["billing", "appointment", "Medical Report", "Complaint", "Procedure"] = Field(
        ...,
        description="Classify the user message as either billing, appointment, medical report, complaint, or procedure."
    )


class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str 


def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
            - 'billing': if it is related to billing.
            - 'appointment': if it is related to appointment scheduling or doctor availability.
            - 'medical report': if it is related to medical reports or test results.
            - 'complaint': if it is related to complaints or issues with services.
            - 'procedure': if it is related to medical procedures or treatments.
            """
        },
        {"role": "user", "content": last_message.content}
    ])

    return {"message_type": result.message_type}


def router(state: State):
    message_type = state.get("message_type", "emergency")
    if message_type == "billing":
        return {"next": "billing"}
    elif message_type == "appointment":
        return {"next": "appointment"}
    elif message_type == "medical report":
        return {"next": "medical report"}
    elif message_type == "complaint":
        return {"next": "complaint"}
    elif message_type == "procedure":
        return {"next": "procedure"}
    else:
        return {"next": "emergency"}
    
def emergency_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """You are a helpful assistant. Send an emergency alert to the medical team and provide a response to the user.
         And you provide two messages: one for the user and one for emergency medical team.
         user_message: <user_message>
         emergency_message: <emergency_message>
         """
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    reply_text = reply.content.strip()

    # Extract boss_message only
    import re
    match = re.search(r"emergency_message\s*:\s*(.+)", reply_text, re.IGNORECASE | re.DOTALL)
    emergency_message = match.group(1).strip() if match else None
    print(f"Emergency message: {emergency_message}")
    
    user_match = re.search(r"user_message\s*:\s*(.+?)(?:\nboss_message|$)", reply_text, re.IGNORECASE | re.DOTALL)
    user_message = user_match.group(1).strip() if user_match else "Our Medical Team is on the way to help you. Please wait for a moment."

    return {"messages": [{"role": "assistant", "content": user_message}]}

def billing_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """You are a helpful assistant. As the feedback is related to billing,
         provide necessary information to create a perfect endpoint of billing -> /billing/{billing_id}.
         You should only return the endpoint like this:
         /billing/12345686745656ghy768

         if user does not provide billing id ask for it
         """
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)

    reply_text = reply.content.strip()
    if reply_text.startswith("/billing/"):
        response = requests.get(f"http://localhost:8000{reply_text}")
        if response.status_code == 200:
            billing_info = response.json()
            return {"messages": [{"role": "assistant", "content": str(billing_info)}]}

    return {"messages": [{"role": "assistant", "content": reply.content}]}


def appointment_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """You are a helpful assistant. As the feedback is related to appointment,
         provide necessary information to create a perfect endpoint of appointment -> /appointments/{department_name}.
            You should only return the endpoint like this:
            /appointments/abcd

            if user does not provide department name ask for it
         """
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)

    reply_text = reply.content.strip()
    if reply_text.startswith("/appointments/"):
        response = requests.get(f"http://localhost:8000{reply_text}")
        if response.status_code == 200:
            appointment_info = response.json()
            return {"messages": [{"role": "assistant", "content": str(appointment_info)}]}


    return {"messages": [{"role": "assistant", "content": reply.content}]}

def medical_report_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """You are a helpful assistant. As the feedback is related to medical report,
         provide necessary information to create a perfect endpoint of medical report -> /medical_report/{report_id}.
            You should only return the endpoint like this:
            /medical_report/12345686745656ghy768

            if user does not provide report id ask for it
         """
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)

    reply_text = reply.content.strip()
    if reply_text.startswith("/medical_report/"):
        response = requests.get(f"http://localhost:8000{reply_text}")
        if response.status_code == 200:
            medical_report_info = response.json()
            return {"messages": [{"role": "assistant", "content": str(medical_report_info)}]}
    
    return {"messages": [{"role": "assistant", "content": reply.content}]}

def complaint_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """You are a helpful assistant. As the feedback is related to complaint,
         provide a response to the user."""
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

def procedure_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """You are a helpful assistant. As the feedback is related to procedure,
         provide a response to the user."""
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}




graph_builder = StateGraph(State)
graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)

graph_builder.add_node("emergency", emergency_agent)
graph_builder.add_node("billing", billing_agent)
graph_builder.add_node("appointment", appointment_agent)
graph_builder.add_node("medical report", medical_report_agent)
graph_builder.add_node("complaint", complaint_agent)
graph_builder.add_node("procedure", procedure_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"emergency": "emergency", "billing": "billing", "appointment": "appointment",
     "medical report": "medical report", "complaint": "complaint", "procedure": "procedure"}
)
graph_builder.add_edge("emergency", END)
graph_builder.add_edge("billing", END)

graph = graph_builder.compile()

def run_chatbot():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("Message: ")
        if user_input == "exit":
            print("Bye")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")


if __name__ == "__main__":
    run_chatbot()