import re
import html



def remove_html_tags(text):
    # Unescape HTML entities
    text = html.unescape(text)
    # Use a regular expression to remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    return text


def format_prompt_list(prompt_list, placeholder_dict, language_list=None):
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
        if language_list:
            prompt = prompt.replace(f"#language#", language_list[index])
        formatted_prompt_list.append(prompt)
    return formatted_prompt_list


def prompt_html(prompt, color):
    return f"<br><br><font color='{color}'>Prompt:<br>{prompt}</font><br><br>"


def field_value_html(field_value_list, color):
    field_value_str = '<br>'.join(field_value_list)

    return f"<font color='{color}'>Choosen values:</font><br>{field_value_str}"
