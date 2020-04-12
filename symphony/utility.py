import json


def format_symphony_message(message: str):
    if not message.startswith('<messageML>'):
        return "<messageML>" + message + "</messageML>"

    return message


def format_symphony_link(url: str):
    return '<a href="' + url + '"/>'


def format_symphony_stream_id(stream_id: str):
    return stream_id.replace('/', '_').replace('+', '-').replace('=', '').strip()


def format_dict_to_mml2(json_obj: dict) -> str:
    json_str = json.dumps(json_obj, indent=4, separators=(',', ': ')).replace('"', '&quot;').replace('\'', '&apos;')

    # apparently you need to include a newline character before the closing code tag. Why? ¯\_(-_-)_/¯
    json_str = "<code>" + json_str + "\n</code>"

    return json_str


# There's no string builder class in Python. Using a list comprehension appears to be the
# most performant way to build long strings. += appending is the worst.
# https://waymoot.org/home/python_string/
def xml_string_builder(xml_tag_list: list) -> str:
    return ''.join(s for s in xml_tag_list)