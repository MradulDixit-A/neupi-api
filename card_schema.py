REQUIRED_FIELDS = {
    "card_id": str,
    "issuer": str,
    "network": str,
    "card_type": str,
    "tier": str,
    "min_income": int,
    "min_credit_score": int,
    "spend_bonus_category": list
}

OPTIONAL_FIELDS = {
    "annual_fee": int,
    "emi_friendly": bool
}


class CardSchemaError(Exception):
    pass


def validate_card(card: dict):
    for field, field_type in REQUIRED_FIELDS.items():
        if field not in card:
            raise CardSchemaError(f"Missing required field: {field}")

        if not isinstance(card[field], field_type):
            raise CardSchemaError(
                f"Field '{field}' must be {field_type.__name__}, got {type(card[field]).__name__}"
            )

    for field, field_type in OPTIONAL_FIELDS.items():
        if field in card and not isinstance(card[field], field_type):
            raise CardSchemaError(
                f"Optional field '{field}' must be {field_type.__name__}"
            )

    return True
