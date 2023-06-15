import re
import html



def remove_html_tags(text):
    # Unescape HTML entities
    text = html.unescape(text)
    # Use a regular expression to remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    return text


def format_prompt_list(prompt_list, placeholder_dict, language_list=None):
    formatted_prompt_list = []
    for i, prompt in enumerate(prompt_list):
        int_i = i
        i = str(i + 1)
        if i in placeholder_dict:
            for key, value in placeholder_dict[i].items():
                prompt = prompt.replace(f"#{key}#", value)
        if language_list:
            prompt = prompt.replace(f"#language#", language_list[int_i])
        formatted_prompt_list.append(prompt)
    return formatted_prompt_list


def prompt_html(prompt, color):
    return f"<font color='{color}'>Prompt: {prompt}</font><br><br>"


def field_value_html(field_value_list, color):
    field_value_str = '<br>'.join(field_value_list)

    return f"<font color='{color}'>Choosen values:</font><br>{field_value_str}"


def find_placeholder(prompt):
    # Matches any string sandwiched by #
    matches = re.findall(r'#(.*?)#', prompt)

    # Ignore keyword placeholders
    ignore_list = ['response', 'field_value', 'language']
    matches = [match for match in matches if match not in ignore_list]

    return matches
