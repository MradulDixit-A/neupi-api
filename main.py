from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from orchestrator import Orchestrator
from rules_config import RULES_CONFIG

app = FastAPI(title="Neupi Analysis Engine")

API_KEY = "NEUPI_API_KEY_2025_SECRET"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mraduldixit.pythonanywhere.com",
        "https://www.mraduldixit.pythonanywhere.com",
        "https://neupi.co.in",
        "https://www.neupi.co.in",
        "http://localhost:5000",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CARDS = [
    {
        "card_id": "amex_mrcc",
        "issuer": "American Express",
        "network": "amex",
        "card_type": "rewards",
        "tier": "mid",
        "min_income": 40000,
        "min_credit_score": 700,
        "spend_bonus_category": ["travel", "online"]
    }
]


class UserProfile(BaseModel):
    email: Optional[EmailStr] = "anonymous@neupi.app"
    age: Optional[int] = 30
    employment_type: str
    monthly_income: int
    monthly_emi: int
    credit_score: Optional[int] = 700
    risk_appetite: Optional[str] = "moderate"
    goals: Optional[List[str]] = []


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/analyze/profile")
def analyze_profile(user: UserProfile, x_api_key: str = Header(None)):

    # 🔓 API-KEY optional for browser calls
    if x_api_key and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # 🔧 Normalize blank lists
    if not user.goals:
        user.goals = []

    normalized_user = {
        "email": user.email,
        "age_group": (
            "18_24" if user.age and user.age < 25 else
            "25_35" if user.age and user.age <= 35 else
            "36_plus"
        ),
        "employment_type": user.employment_type,
        "monthly_income": user.monthly_income,
        "monthly_emi": user.monthly_emi,
        "credit_score_value": user.credit_score or 700,
        "risk_appetite": user.risk_appetite or "moderate",
        "primary_goal": user.goals,
        "preferred_network": "no_preference",
        "top_spend_category": "travel"
    }

    orchestrator = Orchestrator()
    return orchestrator.analyze_with_cards(normalized_user, CARDS)
