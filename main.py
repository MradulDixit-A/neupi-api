from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from credit_card_engine import CreditCardEngine
from rules_config import RULES_CONFIG

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.neupi.co.in",
        "https://neupi.co.in"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CARDS = [
    {
        "card_id": "amex_mrcc",
        "network": "amex",
        "card_type": "rewards",
        "tier": "mid",
        "min_income": 40000,
        "min_credit_score": 700,
        "spend_bonus_category": ["travel_hotels", "online_shopping"]
    }
]

class UserProfile(BaseModel):
    age_group: str
    employment_type: str
    monthly_income: int
    monthly_emi: int
    credit_score_range: str | None = None
    credit_score_value: int | None = 700
    primary_goal: list[str]
    top_spend_category: str
    preferred_network: str

@app.post("/recommend/cards")
def recommend_cards(user: UserProfile):
    engine = CreditCardEngine(RULES_CONFIG)
    return engine.recommend(user.dict(), CARDS)
