from explanation_rules import EXPLANATION_RULES


class ExplainabilityEngine:

    @staticmethod
    def generate(user, card, matched_rules):
        explanations = []

        for rule in matched_rules:
            rule_cfg = EXPLANATION_RULES.get(rule)
            if not rule_cfg:
                continue

            try:
                text = rule_cfg["template"].format(
                    network=card.get("network", "your preferred"),
                    income=user.get("monthly_income", ""),
                    goal=", ".join(user.get("primary_goal", [])) or "your goals",
                    spend_category=user.get("top_spend_category", "your spending habits")
                )
            except Exception:
                text = rule_cfg["template"]

            explanations.append({
                "text": text,
                "priority": rule_cfg.get("priority", 0),
                "type": rule_cfg.get("type", "benefit")
            })

        # Sort best explanations first
        explanations.sort(key=lambda x: x["priority"], reverse=True)

        # Return top 3 only (best UX)
        return explanations[:3]
