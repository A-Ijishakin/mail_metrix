import os 
from dotenv import load_dotenv
import requests

class UnSubscriber:
    def __init__(self): 
        load_dotenv()  # take environment variables from .env. 
        self.HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
        self.HEADERS = {
        "Authorization": f"Bearer {self.HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
        }

    def unsubscribe(self, email):
        url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
        data = {
            "filterGroups": [{
                "filters": [{
                    "propertyName": "email",
                    "operator": "EQ",
                    "value": email
                }]
            }],
            "properties": ["email"]
        }

        response = requests.post(url, json=data, headers=self.HEADERS)
        response.raise_for_status()

        results = response.json().get("results", [])
        if results:
            contact_id = results[0]["id"] 
        else:
            print("No contact found with that email.")
            return None 

        #delete the contact 
        self.delete_contact(contact_id) 

    def delete_contact(self, contact_id):
        url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
        response = requests.delete(url, headers=self.HEADERS)
        if response.status_code == 204:
            print(f"Contact {contact_id} successfully deleted.")
        else:
            print(f"Failed to delete contact: {response.status_code}, {response.text}") 