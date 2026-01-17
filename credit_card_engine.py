from explainability_engine import ExplainabilityEngine


class CreditCardEngine:
    def __init__(self, rules_config):
        self.rules = rules_config

    # -----------------------------
    # CORE USER RISK SIGNALS
    # -----------------------------
    def _emi_ratio(self, user):
        income = max(user.get("monthly_income", 1), 1)
        return user.get("monthly_emi", 0) / income

    def compute_financial_risk(self, user):
        emi_ratio = self._emi_ratio(user)

        if emi_ratio < 0.20:
            return 30, {"emi_ratio": round(emi_ratio, 2), "risk_band": "very_safe"}
        elif emi_ratio < 0.35:
            return 22, {"emi_ratio": round(emi_ratio, 2), "risk_band": "safe"}
        elif emi_ratio < 0.50:
            return 12, {"emi_ratio": round(emi_ratio, 2), "risk_band": "risky"}
        else:
            return 5, {"emi_ratio": round(emi_ratio, 2), "risk_band": "high_risk"}

    def compute_credit_strength(self, user):
        score = user.get("credit_score_value", 700)

        if score >= 770:
            return 35, "excellent"
        elif score >= 730:
            return 28, "strong"
        elif score >= 680:
            return 20, "fair"
        else:
            return 10, "weak"

    def compute_user_strength(self, user):
        risk_score, risk_meta = self.compute_financial_risk(user)
        credit_score, credit_band = self.compute_credit_strength(user)

        return {
            "base_strength": risk_score + credit_score,
            "risk": risk_meta,
            "credit_band": credit_band
        }

    # -----------------------------
    # BEHAVIOUR RISK MODEL
    # -----------------------------
    def compute_behaviour_risk(self, user):
        late_payments = user.get("late_payments_last_12m", 0)
        utilization = user.get("credit_utilization", 0.25)
        inquiries = user.get("recent_credit_inquiries", 0)
        loan_count = user.get("active_loans", 0)
        account_age = user.get("oldest_account_age_years", 1)

        risk_points = 0
        flags = []

        if late_payments == 0:
            risk_points += 15
        elif late_payments <= 2:
            risk_points += 8
            flags.append("mild_late_payment_history")
        else:
            risk_points -= 10
            flags.append("frequent_late_payments")

        if utilization < 0.3:
            risk_points += 10
        elif utilization < 0.6:
            risk_points += 4
            flags.append("medium_utilization")
        else:
            risk_points -= 8
            flags.append("high_utilization_risk")

        if inquiries > 3:
            risk_points -= 6
            flags.append("high_recent_credit_activity")

        if loan_count > 4:
            risk_points -= 5
            flags.append("multiple_active_loans")

        if account_age < 1:
            risk_points -= 4
            flags.append("thin_credit_file")

        band = (
            "excellent" if risk_points >= 20 else
            "stable" if risk_points >= 10 else
            "watch" if risk_points >= 0 else
            "risky"
        )

        return {
            "behaviour_score": risk_points,
            "behaviour_band": band,
            "behaviour_flags": flags
        }

    # -----------------------------
    # BNPL RISK MODEL
    # -----------------------------
    def compute_bnpl_risk(self, user):
        bnpl_usage = user.get("bnpl_monthly_spend_ratio", 0.0)
        bnpl_active_loans = user.get("bnpl_active_loans", 0)
        bnpl_rollovers = user.get("bnpl_rollovers_last_6m", 0)
        bnpl_on_time = user.get("bnpl_on_time_rate", 1.0)

        risk = 0
        notes = []

        if bnpl_usage < 0.15:
            risk += 10
        elif bnpl_usage < 0.35:
            risk += 4
            notes.append("moderate_bnpl_dependency")
        else:
            risk -= 8
            notes.append("high_bnpl_dependency")

        if bnpl_rollovers == 0:
            risk += 8
        elif bnpl_rollovers <= 2:
            risk += 2
            notes.append("occasional_bnpl_rollover")
        else:
            risk -= 10
            notes.append("frequent_bnpl_rollovers")

        if bnpl_active_loans > 3:
            risk -= 6
            notes.append("bnpl_stack_risk")

        if bnpl_on_time < 0.8:
            risk -= 7
            notes.append("bnpl_repayment_concerns")

        band = (
            "responsible" if risk >= 18 else
            "controlled" if risk >= 10 else
            "watch" if risk >= 0 else
            "high_risk"
        )

        return {
            "bnpl_score": risk,
            "bnpl_band": band,
            "bnpl_flags": notes
        }

    # -----------------------------
    # COMPOSITE PROFILE
    # -----------------------------
    def compute_full_risk_profile(self, user):
        strength = self.compute_user_strength(user)
        behaviour = self.compute_behaviour_risk(user)
        bnpl = self.compute_bnpl_risk(user)

        composite = (
            strength["base_strength"] +
            behaviour["behaviour_score"] +
            bnpl["bnpl_score"]
        )

        return {
            "composite_score": composite,
            "strength": strength,
            "behaviour": behaviour,
            "bnpl": bnpl
        }

    # -----------------------------
    # FILTERS
    # -----------------------------
    def apply_hard_filters(self, user, cards):
        filtered = []
        emi_ratio = self._emi_ratio(user)

        for card in cards:
            allowed = True
            card["_risk_penalty"] = 0

            if user["age_group"] == "18_24" and card["tier"] in ["premium", "super_premium"]:
                allowed = False

            if user["employment_type"] in ["student", "retired"] and card["tier"] not in ["entry", "secured"]:
                allowed = False

            if user.get("credit_score_range") == "below_650" and card["tier"] not in ["entry", "secured"]:
                allowed = False

            if emi_ratio > 0.30 and card["tier"] in ["premium", "super_premium"]:
                card["_risk_penalty"] = 10

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

        allowed = network_map.get(pref, [])
        return [c for c in cards if c.get("network") in allowed]

    # -----------------------------
    # SCORING ENGINE
    # -----------------------------
    def score_cards(self, user, cards):
        scored = []
        weights = self.rules["scoring_weights"]
        emi_ratio = self._emi_ratio(user)

        risk_profile = self.compute_full_risk_profile(user)

        goal_types = []
        for g in user.get("primary_goal", []):
            goal_types.extend(self.rules["goal_card_type_map"].get(g, []))

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

            score -= card.get("_risk_penalty", 0)

            score += max(min(risk_profile["composite_score"] / 10, 12), -12)

            if score >= self.rules["minimum_score_to_show"]:
                explanations = ExplainabilityEngine.generate(user, card, matched_rules)

                scored.append({
                    "card": card,
                    "score": round(score, 2),
                    "why_this_card": explanations,
                    "risk_profile": risk_profile
                })

        return sorted(scored, key=lambda x: x["score"], reverse=True)

    # -----------------------------
    # FINAL RECOMMENDATION
    # -----------------------------
    def recommend(self, user, cards):
        cards = self.apply_hard_filters(user, cards)
        cards = self.apply_network_filter(user, cards)

        scored = self.score_cards(user, cards)

        # fallback cards
        if len(scored) < self.rules["top_results"]:
            fillers = sorted(cards, key=lambda c: c.get("min_income", 0))
            for c in fillers:
                if len(scored) >= self.rules["top_results"]:
                    break

                explanations = ExplainabilityEngine.generate(
                    user, c, ["alternative_option"]
                )

                scored.append({
                    "card": c,
                    "score": 10,
                    "why_this_card": explanations
                })

        top = scored[:self.rules["top_results"]]
        alternatives = scored[self.rules["top_results"]:]

        confidence = round(
            sum(1 for t in top if t["score"] >= 60) / len(top),
            2
        )

        return {
            "eligible": True,
            "confidence_score": confidence,
            "primary": top,
            "alternatives": alternatives
        }
