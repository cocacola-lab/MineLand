import os

def load_prompt(filename: str):
    if not filename.endswith(".txt"):
        filename += ".txt"
    directory = os.path.dirname(__file__)
    filepath = os.path.join(directory, filename)

    try:
        with open(filepath, "r") as f:
            prompt = f.read()
        return prompt
    except Exception as e:
        print(f"Error loading prompt from {filepath}: {e}")
        return ""
