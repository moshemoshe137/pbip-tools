import json
import sys

from pbi_pbit_filters.json_types import JSONType


def format_nested_json_strings(json_data: JSONType) -> JSONType:
    if not isinstance(json_data, dict | list):
        return json_data

    if isinstance(json_data, list):
        # Turn it into a `dict`.
        json_data = dict(enumerate(json_data))

    index = range(len(json_data)) if isinstance(json_data, list) else json_data.keys()
    for list_position_or_dict_key in index:
        value = json_data[list_position_or_dict_key]
        if isinstance(value, dict | list):
            json_data[list_position_or_dict_key] = format_nested_json_strings(value)
        elif isinstance(value, str):
            try:
                parsed_value = json.loads(value)
                formatted_value = format_nested_json_strings(parsed_value)
                json_data[list_position_or_dict_key] = formatted_value
            except json.JSONDecodeError:
                continue
    return json_data


json_data = json.loads(sys.stdin.read())
formatted_data = format_nested_json_strings(json_data)
sys.stdout.write(json.dumps(formatted_data, ensure_ascii=False, indent=4))
