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
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# CARD MASTER DATA
# -------------------
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

# -------------------
# REQUEST SCHEMA
# -------------------
class UserProfile(BaseModel):
    email: EmailStr
    age: int
    employment_type: str
    monthly_income: int
    monthly_emi: int
    credit_score: Optional[int] = 700
    risk_appetite: str
    goals: List[str]

# -------------------
# ROOT (health check)
# -------------------
@app.get("/")
def root():
    return {"status": "ok"}

# -------------------
# MAIN ANALYSIS API
# -------------------
@app.post("/analyze/profile")
def analyze_profile(
    user: UserProfile,
    x_api_key: str = Header(None)
):
    try:
        if x_api_key != API_KEY:
            raise HTTPException(status_code=403, detail="Invalid API key")

        normalized_user = {
            "email": user.email,
            "age_group": (
                "18_24" if user.age < 25 else
                "25_35" if user.age <= 35 else
                "36_plus"
            ),
            "employment_type": user.employment_type,
            "monthly_income": user.monthly_income,
            "monthly_emi": user.monthly_emi,
            "credit_score_value": user.credit_score or 700,
            "credit_score_range": (
                "excellent" if (user.credit_score or 700) >= 750 else
                "good" if (user.credit_score or 700) >= 700 else
                "average"
            ),
            "risk_appetite": user.risk_appetite,
            "primary_goal": user.goals,
            "preferred_network": "no_preference",
            "top_spend_category": "travel"
        }

        orchestrator = Orchestrator()
        result = orchestrator.analyze_with_cards(normalized_user, CARDS)

        return result

    except Exception as e:
        print("🔥 INTERNAL ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
