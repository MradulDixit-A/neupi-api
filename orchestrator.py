from credit_card_engine import CreditCardEngine
from rules_config import RULES_CONFIG


class Orchestrator:
    def __init__(self):
        self.card_engine = CreditCardEngine(RULES_CONFIG)

    # -------------------------------------------------
    # BASE PROFILE (kept minimal — used by UI summary)
    # -------------------------------------------------
    def analyze_profile(self, user: dict) -> dict:
        return {
            "status": "success",
            "summary": {
                "risk": user["risk_appetite"],
                "primary_goal": user.get("primary_goal", []),
                "income": user["monthly_income"]
            }
        }

    # -------------------------------------------------
    #  HEALTH SCORE ENGINE
    # -------------------------------------------------
    def _build_health_score(self, user: dict) -> dict:
        """
        Derives a 0–100 Financial Health Score using the
        same risk signals used in recommendation logic.
        """

        strength = self.card_engine.compute_user_strength(user)
        behaviour = self.card_engine.compute_behaviour_risk(user)
        bnpl = self.card_engine.compute_bnpl_risk(user)

        # Weighted composite — tunable in RULES_CONFIG later
        score = (
            strength["base_strength"] +
            behaviour["behaviour_score"] +
            bnpl["bnpl_score"]
        )

        # clamp into 0–100 band
        score = max(0, min(score, 100))

        band = (
            "Excellent" if score >= 80 else
            "Good" if score >= 65 else
            "Fair" if score >= 50 else
            "Needs Attention"
        )

        breakdown = [
            {
                "label": "Financial Strength",
                "value": strength["base_strength"],
                "source": strength
            },
            {
                "label": "Payment Behaviour",
                "value": behaviour["behaviour_score"],
                "source": behaviour
            },
            {
                "label": "BNPL Risk",
                "value": bnpl["bnpl_score"],
                "source": bnpl
            }
        ]

        return {
            "score": round(score),
            "band": band,
            "breakdown": breakdown
        }

    # -------------------------------------------------
    #  MAIN PIPELINE
    # -------------------------------------------------
    def analyze_with_cards(self, user: dict, cards: list) -> dict:
        profile = self.analyze_profile(user)

        # 🔹 Compute full risk + health meta
        health = self._build_health_score(user)

        # 🔹 Card Recommendations (already risk-aware)
        card_results = self.card_engine.recommend(user, cards)

        # Attach outputs
        profile["health_score"] = health["score"]
        profile["health_band"] = health["band"]
        profile["health_breakdown"] = health["breakdown"]

        profile["risk_profile"] = {
            "strength": health["breakdown"][0]["source"],
            "behaviour": health["breakdown"][1]["source"],
            "bnpl": health["breakdown"][2]["source"]
        }

        profile["recommended_cards"] = card_results

        return profile
