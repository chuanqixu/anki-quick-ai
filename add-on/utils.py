def format_prompt_list(prompt_list, placeholder_dict):
    promp_index_placeholder_value_dict = {}
    for placeholder, promp_index_value_dict in placeholder_dict.items():
        for index, value in promp_index_value_dict.items():
            index = int(index)
            if index in promp_index_placeholder_value_dict:
                promp_index_placeholder_value_dict[index][placeholder] = value
            else:
                promp_index_placeholder_value_dict[index] = {placeholder: value}
    
    formatted_prompt_list = []
    for index, prompt in enumerate(prompt_list):
        if index in promp_index_placeholder_value_dict:
            for key, value in promp_index_placeholder_value_dict[index].items():
                prompt = prompt.replace(f"#{key}#", value)
            formatted_prompt_list.append(prompt)
        else:
            formatted_prompt_list.append(prompt)
    return formatted_prompt_list
