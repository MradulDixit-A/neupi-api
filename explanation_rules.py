EXPLANATION_RULES = {
    "network_match": {
        "template": "You prefer using cards on the {network} network, which this card supports well.",
        "priority": 3,
        "type": "benefit"
    },

    "income_match": {
        "template": "With a monthly income of ₹{income}, you comfortably meet this card’s eligibility criteria.",
        "priority": 4,
        "type": "benefit"
    },

    "credit_score_match": {
        "template": "Your credit score places you in a strong approval range for this card.",
        "priority": 5,
        "type": "benefit"
    },

    "goal_match": {
        "template": "This card aligns well with your goal of {goal}, offering benefits that match your priorities.",
        "priority": 5,
        "type": "benefit"
    },

    "spend_category_match": {
        "template": "Since you spend more on {spend_category}, this card can help you earn better rewards in that category.",
        "priority": 4,
        "type": "benefit"
    },

    "low_emi_bonus": {
        "template": "Your current EMI commitments are well within safe limits, which improves your approval chances.",
        "priority": 4,
        "type": "benefit"
    },

    "high_emi_penalty": {
        "template": "Your EMI commitments are relatively high, so premium cards may be harder to manage comfortably.",
        "priority": 2,
        "type": "warning"
    },

    "high_fee_penalty": {
        "template": "This card has a higher annual fee, which may not be ideal at your current income level.",
        "priority": 2,
        "type": "tradeoff"
    },

    "alternative_option": {
        "template": "This card is suggested as a safer alternative based on your current financial profile.",
        "priority": 1,
        "type": "fallback"
    }
}
