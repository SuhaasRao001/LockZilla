import requests

class EmailSender:
    def __init__(self, api_key, api_host):
        self.api_key = api_key
        self.api_host = api_host
        self.url = "https://rapidmail.p.rapidapi.com/"

    def send_password_email(self, email_recipient, password):
        """Send the login password to the user's email."""
        payload = {
            "ishtml": "false",
            "sendto": email_recipient,
            "name": "Lockzilla User",
            "replyTo": "admin@go-mail.us.to",
            "title": "Your Lockzilla Login Password",
            "body": f"Hello,\n\nYour login password for Lockzilla is: {password}\n\nPlease keep it secure."
        }
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
            "Content-Type": "application/json"
        }

        response = requests.post(self.url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send email: {response.status_code}, {response.text}")
