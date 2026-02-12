import os
import secrets
import json
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
SECRETS_FILE = os.path.join(os.path.dirname(__file__), '../data/secrets.json')

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_secret_key() -> str:
    """
    Retrieves the API Key from environment variable or secrets file.
    Generates a new one if not found.
    """
    # 1. Check Environment Variable
    env_key = os.environ.get("JAPANESE_APP_API_KEY")
    if env_key:
        return env_key

    # 2. Check Secrets File
    if os.path.exists(SECRETS_FILE):
        try:
            with open(SECRETS_FILE, 'r') as f:
                data = json.load(f)
                if "api_key" in data:
                    return data["api_key"]
        except Exception as e:
            print(f"Error reading secrets file: {e}")

    # 3. Generate New Key
    new_key = secrets.token_urlsafe(32)
    print(f"Generating new API Key: {new_key}")

    # Save to file
    try:
        os.makedirs(os.path.dirname(SECRETS_FILE), exist_ok=True)
        with open(SECRETS_FILE, 'w') as f:
            json.dump({"api_key": new_key}, f, indent=2)
        print(f"API Key saved to {SECRETS_FILE}")
    except Exception as e:
        print(f"Error saving secrets file: {e}")

    return new_key

# Load key once at startup
API_KEY = get_secret_key()

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key",
        )
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key
