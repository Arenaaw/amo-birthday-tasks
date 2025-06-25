import os
import requests
from datetime import datetime, timedelta

AMO_CLIENT_ID = os.getenv('AMO_CLIENT_ID')
AMO_CLIENT_SECRET = os.getenv('AMO_CLIENT_SECRET')
AMO_REDIRECT_URI = os.getenv('AMO_REDIRECT_URI')
AMO_REFRESH_TOKEN = os.getenv('AMO_REFRESH_TOKEN')
AMO_DOMAIN = os.getenv('AMO_DOMAIN')

def get_access_token():
    url = f"https://{AMO_DOMAIN}/oauth2/access_token"
    data = {
        "client_id": AMO_CLIENT_ID,
        "client_secret": AMO_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": AMO_REFRESH_TOKEN,
        "redirect_uri": AMO_REDIRECT_URI
    }
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()

def get_contacts(access_token):
    url = f"https://{AMO_DOMAIN}/api/v4/contacts"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"with": "custom_fields_values"}
    contacts = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        contacts.extend(data["_embedded"]["contacts"])
        url = data["_links"].get("next", {}).get("href")
    return contacts

def get_birthday_field(contact):
    for field in contact.get("custom_fields_values", []):
        if field.get("field_code") == "BIRTHDAY":
            return field.get("values")[0].get("value")
    return None

def create_task(access_token, contact_id, text):
    url = f"https://{AMO_DOMAIN}/api/v4/tasks"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "entity_id": contact_id,
        "entity_type": "contacts",
        "text": text,
        "complete_till": int((datetime.now() + timedelta(days=60)).timestamp()),
        "task_type": 1
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def main():
    tokens = get_access_token()
    access_token = tokens["access_token"]

    contacts = get_contacts(access_token)
    today = datetime.now()
    target_date = today + timedelta(days=60)
    target_md = target_date.strftime("%m-%d")

    for contact in contacts:
        birthday = get_birthday_field(contact)
        if birthday and birthday[5:10] == target_md:
            create_task(access_token, contact["id"], f"Подготовиться к дню рождения клиента {contact['name']}")

if __name__ == "__main__":
    main()