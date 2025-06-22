from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Dict, Any
from bson import ObjectId

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient("mongodb+srv://ataur:1122@cluster0.0rjg29f.mongodb.net/")
db = client["healthcare-customer-service"]
appointments_collection = db["appointments"]
billing_collection = db["billing"]
medical_report_collection = db["medical_report"]
complaint_collection = db["complaint"]
biiling_query_collection = db["billing_query"]


class Complaint(BaseModel):
    user_id: str
    complaint_text: str
@app.post("/complaint")
def create_complaint(complaint: Complaint):
    complaint_dict = complaint.dict()
    complaint_dict["status"] = "pending"
    result = complaint_collection.insert_one(complaint_dict)
    return {"message": "Complaint created successfully", "complaint_id": str(result.inserted_id)}

@app.get("/billing/{billing_id}")
def get_billing(billing_id: str):
    billing_id = ObjectId(billing_id)
    billing = billing_collection.find_one({"_id": billing_id})
    billing = convert_objectid(billing)
    if billing:
        return {"billing": billing}
    else:
        return {"message": "Billing not found"}
    
    
def convert_objectid(document):
    document["_id"] = str(document["_id"])
    return document

@app.get("/appointments/{department_name}")
def get_appointments(department_name: str):
    appointments_cursor = appointments_collection.find({"department_name": department_name})
    appointments = [convert_objectid(app) for app in appointments_cursor]
    if appointments:
        return {"appointments": appointments}
    else:
        return {"message": "No appointments found for this department"}
    
@app.get("/medical_report/{report_id}")
def get_medical_report(report_id: str):
    report_id = ObjectId(report_id)
    medical_report = medical_report_collection.find_one({"_id": report_id})
    medical_report = convert_objectid(medical_report)
    if medical_report:
        return {"medical_report": medical_report}
    else:
        return {"message": "Medical report not found"}
