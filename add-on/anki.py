def get_note_field_value_list(collection, browse_cmd, note_field_config):
    note_id_list = collection.find_notes(browse_cmd)

    field_value_list = []
    for note_id in note_id_list:
        note = collection.get_note(note_id)
        note_type = note.note_type()["name"]
        if note_type in note_field_config:
            for field_name in note_field_config[note_type]:
                if field_name in note:
                    field_value_list.append(note[field_name])
        elif "Other Note Type" in note_field_config:
            for field_name in note_field_config["Other Note Type"]:
                if field_name in note:
                    field_value_list.append(note[field_name])

    return field_value_list


def get_note_type_names_fields_dict(collection):
    note_type_name_id_list = collection.models.all_names_and_ids()

    note_type_names_fields_dict = {}
    for note_type in note_type_name_id_list:
        note_type_name = note_type.name
        note_type_id = note_type.id

        note_type_names_fields_dict[note_type_name] = [field["name"] for field in collection.models.get(note_type_id)["flds"]]

    return note_type_names_fields_dict
