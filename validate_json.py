import json

def validate_json_file(filepath):
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        print(f"{filepath} is valid JSON.")
    except json.JSONDecodeError as e:
        print(f"Error parsing {filepath}: {e}")

if __name__ == "__main__":
    validate_json_file('hospitals.json')
    validate_json_file('precautions.json')
