import json
import sys

from pbi_pbip_filters.json_types import JSONType


def smudge_json(data: JSONType) -> JSONType:
    """
    Converts certain keys' values back to JSON strings for use by Power BI.
    """

    # Define the keys that need to be converted to JSON strings
    conditional_keys = {"config", "filters", "value"}

    if isinstance(data, dict):
        for key, value in data.items():
            if key in conditional_keys and isinstance(value, dict | list):
                # Convert these keys back to JSON strings
                data[key] = json.dumps(value, ensure_ascii=False, indent=0)
            else:
                # Recursively apply the smudge operation
                data[key] = smudge_json(value)
    elif isinstance(data, list):
        data = [smudge_json(item) for item in data]

    return data


if __name__ == "__main__":
    # Read JSON data from stdin
    input_json = json.loads(sys.stdin.read())

    # Process the JSON data
    output_json = smudge_json(input_json)

    # Output the formatted JSON
    sys.stdout.write(json.dumps(output_json, ensure_ascii=False, indent=4))
