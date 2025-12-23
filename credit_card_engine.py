from explainability_engine import ExplainabilityEngine


class CreditCardEngine:
    def __init__(self, rules_config):
        self.rules = rules_config

    def _emi_ratio(self, user):
        if user["monthly_income"] == 0:
            return 1
        return user["monthly_emi"] / user["monthly_income"]

    def apply_hard_filters(self, user, cards):
        filtered = []
        emi_ratio = self._emi_ratio(user)

        for card in cards:
            allowed = True

            if user["age_group"] == "18_24" and card["tier"] in ["premium", "super_premium"]:
                allowed = False

            if user["employment_type"] in ["student", "retired"] and card["tier"] not in ["entry", "secured"]:
                allowed = False

            if user.get("credit_score_range") == "below_650" and card["tier"] not in ["entry", "secured"]:
                allowed = False

            if emi_ratio > 0.3 and card["tier"] in ["premium", "super_premium"]:
                allowed = False

            if allowed:
                filtered.append(card)

        return filtered

    def apply_network_filter(self, user, cards):
        pref = user["preferred_network"]

        if pref == "no_preference":
            return cards

        network_map = {
            "visa_mastercard": ["visa", "mastercard"],
            "amex": ["amex"],
            "rupay": ["rupay"]
        }

        allowed_networks = network_map.get(pref, [])
        return [c for c in cards if c["network"] in allowed_networks]

    def score_cards(self, user, cards):
        scored = []
        weights = self.rules["scoring_weights"]
        emi_ratio = self._emi_ratio(user)

        goal_types = []
        for goal in user.get("primary_goal", []):
            goal_types.extend(self.rules["goal_card_type_map"].get(goal, []))

        for card in cards:
            score = 0
            matched_rules = []

            if card["network"] == user["preferred_network"]:
                score += weights["network_match"]
                matched_rules.append("network_match")

            if user["monthly_income"] >= card["min_income"]:
                score += weights["income_match"]
                matched_rules.append("income_match")

            if user.get("credit_score_value", 700) >= card["min_credit_score"]:
                score += weights["credit_score_match"]
                matched_rules.append("credit_score_match")

            if card["card_type"] in goal_types:
                score += weights["goal_match"]
                matched_rules.append("goal_match")

            if user["top_spend_category"] in card.get("spend_bonus_category", []):
                score += weights["spend_category_match"]
                matched_rules.append("spend_category_match")

            if emi_ratio < 0.3:
                score += weights["low_emi_bonus"]
                matched_rules.append("low_emi_bonus")

            if score >= self.rules["minimum_score_to_show"]:
                explanations = ExplainabilityEngine.generate(
                    user=user,
                    card=card,
                    matched_rules=matched_rules
                )

                scored.append({
                    "card": card,
                    "score": score,
                    "why_this_card": explanations
                })

        return sorted(scored, key=lambda x: x["score"], reverse=True)

    def recommend(self, user, cards):
        cards = self.apply_hard_filters(user, cards)
        cards = self.apply_network_filter(user, cards)

        scored = self.score_cards(user, cards)

        if not scored:
            return {
                "eligible": False,
                "message": "Entry-level or secured cards are more suitable right now."
            }

        top = scored[:self.rules["top_results"]]
        alternatives = scored[self.rules["top_results"]:]

        confidence = round(
            sum(1 for t in top if t["score"] >= 70) / len(top),
            2
        )

        return {
            "eligible": True,
            "confidence_score": confidence,
            "primary": top,
            "alternatives": alternatives
        }
