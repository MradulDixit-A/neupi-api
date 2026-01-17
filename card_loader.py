import json
from card_schema import validate_card, CardSchemaError


def load_cards_from_json(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            cards = json.load(f)

        if not isinstance(cards, list):
            raise ValueError("Card master file must contain a list")

        valid_cards = []

        for idx, card in enumerate(cards):
            try:
                validate_card(card)
                valid_cards.append(card)
            except CardSchemaError as e:
                print(f"❌ Card #{idx + 1} invalid: {e}")

        if not valid_cards:
            raise ValueError("No valid cards found in master file")

        print(f"✅ Loaded {len(valid_cards)} valid cards")

        return valid_cards

    except Exception as e:
        print("🔥 Failed to load card master:", str(e))
        raise
