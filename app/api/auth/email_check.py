import requests
from fastapi import HTTPException

from api.core.config import API_KEY


def check_email(email: str):
    api_key = API_KEY

    email_to_check = email

    url = f"https://api.hunter.io/v2/email-verifier?email={email_to_check}&api_key={api_key}"

    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        result = response.json()
        if result.get('data', {}).get('status') == 'valid':
            return True

        elif result.get('data', {}).get('status') == 'invalid':

            raise HTTPException(status_code=400, detail="Invalid email address")
        else:

            raise HTTPException(status_code=500, detail="Email verification failed")
    else:

        raise HTTPException(status_code=500, detail="Email Hunter API request failed")