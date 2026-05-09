import requests

API_KEY = "AIzaSyD8aXnKY2AQKFfcYT2UD51SqsuRpHXCnlM"
URL = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

def list_models():
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("Available Models:")
            for m in models:
                print(f"- {m['name']}")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    list_models()
