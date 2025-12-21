RULES_CONFIG = {
    "minimum_score_to_show": 60,
    "top_results": 2,
    "scoring_weights": {
        "network_match": 20,
        "income_match": 20,
        "credit_score_match": 25,
        "goal_match": 20,
        "spend_category_match": 15,
        "low_emi_bonus": 10
    },
    "goal_card_type_map": {
        "save_money": ["cashback"],
        "earn_rewards": ["rewards"],
        "travel": ["travel"],
        "fuel": ["fuel"],
        "tax_saving": ["low_fee"]
    }
}
