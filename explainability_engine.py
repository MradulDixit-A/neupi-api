from explanation_rules import EXPLANATION_RULES


class ExplainabilityEngine:
    @staticmethod
    def generate(user, card, matched_rules):
        explanations = []

        for rule_key in matched_rules:
            rule = EXPLANATION_RULES.get(rule_key)
            if not rule:
                continue

            text = rule["template"].format(
                network=card.get("network", "").upper(),
                income=user.get("monthly_income"),
                goal=", ".join(user.get("primary_goal", [])),
                spend_category=user.get("top_spend_category", "").replace("_", " ")
            )

            explanations.append(text)

        return explanations
