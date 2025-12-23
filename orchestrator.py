from credit_card_engine import CreditCardEngine
from rules_config import RULES_CONFIG


class Orchestrator:
    def __init__(self):
        self.card_engine = CreditCardEngine(RULES_CONFIG)

    # 🔹 EXISTING METHOD (DO NOT TOUCH)
    def analyze_profile(self, user: dict) -> dict:
        return {
            "status": "success",
            "profile_score": 100,
            "summary": {
                "risk": user["risk_appetite"],
                "primary_goal": user.get("primary_goal", []),
                "income": user["monthly_income"]
            }
        }

    # 🔹 NEW METHOD (SAFE ADDITION)
    def analyze_with_cards(self, user: dict, cards: list) -> dict:
        profile = self.analyze_profile(user)

        card_results = self.card_engine.recommend(user, cards)

        profile["recommended_cards"] = card_results
        return profile
