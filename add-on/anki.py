import json, os


def get_note_field_value_list(collection, browse_cmd, note_field):
    card_id_list = collection.find_cards(browse_cmd)
    with open(os.path.join(os.path.dirname(__file__), "test"), "w") as f:
        json.dump([str(x) for x in card_id_list], f)
    field_value_list = [collection.get_card(card_id).note()[note_field] for card_id in card_id_list]
    return field_value_list
