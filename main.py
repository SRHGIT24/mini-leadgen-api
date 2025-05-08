from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from faker import Faker
import random
import sqlite3

app = FastAPI()
fake = Faker()

# --- Database Setup (SQLite for simplicity) ---
conn = sqlite3.connect('leads.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    title TEXT,
                    email TEXT,
                    company TEXT,
                    industry TEXT
                )''')
conn.commit()

# --- Pydantic Schemas ---
class LeadRequest(BaseModel):
    company_name: str
    industry: str

class MessageRequest(BaseModel):
    lead_name: str
    company_name: str

class Lead(BaseModel):
    name: str
    title: str
    email: str
    company: str
    industry: str

# --- Helper to Generate Fake Leads ---
def generate_fake_leads(company_name: str, industry: str, count=3):
    leads = []
    for _ in range(count):
        name = fake.name()
        title = random.choice(["Head of Growth", "Marketing Lead", "Business Dev Manager"])
        email = fake.email()
        leads.append({
            "name": name,
            "title": title,
            "email": email,
            "company": company_name,
            "industry": industry
        })
    return leads

# --- Routes ---
@app.post("/generate-leads", response_model=List[Lead])
def generate_leads(request: LeadRequest):
    leads = generate_fake_leads(request.company_name, request.industry)
    for lead in leads:
        cursor.execute('''INSERT INTO leads (name, title, email, company, industry)
                          VALUES (?, ?, ?, ?, ?)''',
                       (lead['name'], lead['title'], lead['email'], lead['company'], lead['industry']))
    conn.commit()
    return leads

@app.post("/compose-message")
def compose_message(request: MessageRequest):
    message = f"Hi {request.lead_name}, I came across your work at {request.company_name} and was really impressed. I'd love to connect and explore how we could collaborate."
    return {"message": message}

@app.get("/leads", response_model=List[Lead])
def get_leads():
    cursor.execute("SELECT name, title, email, company, industry FROM leads")
    rows = cursor.fetchall()
    return [Lead(name=r[0], title=r[1], email=r[2], company=r[3], industry=r[4]) for r in rows]
