from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from openai import OpenAI
from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

#load env file
load_dotenv()

# -------------------
# OpenAI Setup
# -------------------
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
# -------------------
# PostgreSQL DB Setup
# -------------------
# Replace with your actual credentials
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# -------------------
# Ticket Model
# -------------------
class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    grievance_text = Column(Text, nullable=False)
    category = Column(String(50))
    assigned_team = Column(String(50))
    status = Column(String(20))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# Uncomment if you want SQLAlchemy to create table automatically
# Base.metadata.create_all(bind=engine)

# -------------------
# FastAPI App
# -------------------
app = FastAPI()

class TicketRequest(BaseModel):
    grievance_text: str

@app.post("/tickets")
def create_ticket(req: TicketRequest):
    # LLM Classification
    prompt = f"Classify the grievance into one of [IT, HR, Payroll, Facilities]. Grievance: \"{req.grievance_text}\". Only reply with the category."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a machine that assigns the ticket to the respective team."},
                  {"role":"user", "content":prompt}]
    )
    category = response.choices[0].message.content

    # Create ticket
    ticket = Ticket(
        grievance_text=req.grievance_text,
        category=category,
        assigned_team=f"{category} Team",
        status="OPEN",
        created_at=datetime.utcnow()
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    return {
        "id": ticket.id,
        "grievance_text": ticket.grievance_text,
        "category": ticket.category,
        "assigned_team": ticket.assigned_team,
        "status": ticket.status,
        "created_at": ticket.created_at
    }

@app.get("/tickets")
def get_tickets():
    tickets = session.query(Ticket).all()
    return [
        {
            "id": t.id,
            "grievance_text": t.grievance_text,
            "category": t.category,
            "assigned_team": t.assigned_team,
            "status": t.status,
            "created_at": t.created_at
        }
        for t in tickets
    ]

# -------------------
# CORS (React frontend)
# -------------------
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
