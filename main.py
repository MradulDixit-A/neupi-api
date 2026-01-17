from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
import json

from orchestrator import Orchestrator

app = FastAPI(title="Neupi Analysis Engine")

API_KEY = "NEUPI_API_KEY_2025_SECRET"

# -----------------------------
#  CORS
# -----------------------------
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

# -----------------------------
#  LOAD CARD MASTER DATA
# -----------------------------
def load_cards():
    try:
        with open("cards_master.json", "r", encoding="utf-8") as f:
            cards = json.load(f)
            print(f"✅ Loaded {len(cards)} cards")
            return cards
    except Exception as e:
        print("❌ Failed to load cards_master.json:", e)
        return []

CARDS = load_cards()

# -----------------------------
#  USER INPUT MODEL (NEW SCHEMA)
# -----------------------------
class UserProfile(BaseModel):
    email: Optional[EmailStr] = "anonymous@neupi.app"

    age_group: str
    employment_type: str

    monthly_income: int
    monthly_emi: int

    credit_score_range: str

    repayment_behavior: str
    bnpl_usage: str

    primary_goal: List[str]

    spend_profile: Dict[str, int]

    annual_fee_comfort: str

# -----------------------------
#  HELPERS (SCHEMA → ENGINE)
# -----------------------------
credit_score_map = {
    "below_650": 620,
    "650_700": 675,
    "700_750": 725,
    "750_plus": 780
}

repayment_map = {
    "pay_full": 0,
    "sometimes_min_due": 2,
    "frequent_min_due": 5
}

bnpl_map = {
    "no_bnpl": 0.05,
    "occasional_bnpl": 0.25,
    "regular_bnpl": 0.6
}

fee_map = {
    "prefer_zero_fee": "low",
    "fee_ok_if_benefits_good": "medium",
    "comfortable_with_premium_cards": "high"
}

def extract_top_spend(spend_profile: Dict[str, int]) -> str:
    if not spend_profile:
        return "online_shopping"
    return max(spend_profile, key=spend_profile.get)

# -----------------------------
#  ROUTES
# -----------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "cards_loaded": len(CARDS)
    }

@app.post("/analyze/profile")
def analyze_profile(user: UserProfile, x_api_key: str = Header(None)):

    # API key check (optional)
    if x_api_key and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    normalized_user = {
        "email": user.email,

        "age_group": user.age_group,
        "employment_type": user.employment_type,

        "monthly_income": user.monthly_income,
        "monthly_emi": user.monthly_emi,

        "credit_score_range": user.credit_score_range,
        "credit_score_value": credit_score_map.get(user.credit_score_range, 700),

        "risk_appetite": "moderate",

        "primary_goal": user.primary_goal or [],

        "preferred_network": "no_preference",

        "top_spend_category": extract_top_spend(user.spend_profile),

        # Behaviour model
        "late_payments_last_12m": repayment_map.get(user.repayment_behavior, 1),
        "credit_utilization": 0.35,

        # BNPL model
        "bnpl_monthly_spend_ratio": bnpl_map.get(user.bnpl_usage, 0.2),
        "bnpl_active_loans": 1 if user.bnpl_usage != "no_bnpl" else 0,
        "bnpl_rollovers_last_6m": 1 if user.bnpl_usage == "regular_bnpl" else 0,
        "bnpl_on_time_rate": 0.85,

        # Fee sensitivity
        "annual_fee_comfort": fee_map.get(user.annual_fee_comfort, "medium")
    }

    orchestrator = Orchestrator()
    return orchestrator.analyze_with_cards(normalized_user, CARDS)
