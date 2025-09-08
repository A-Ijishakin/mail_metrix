import os
from flask import Flask, request, jsonify
import gspread
import json
import datetime
from unsubscribe import UnSubscriber
from oauth2client.service_account import ServiceAccountCredentials
from spread_sheet_utils import SpreadSheetUtils

# Setup Google Sheets client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Load the credentials from environment variable
creds_json = os.environ.get("GOOGLE_CREDS")
creds_dict = json.loads(creds_json)
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Email Mastersheet").sheet1  # Adjust as needed

app = Flask(__name__)

# This stores replies into a local JSON file
@app.route('/mailgun/inbound', methods=['POST'])
def receive_reply():
    data = request.form.to_dict()
    msg = {
        "from": data.get('sender'),
        "to": data.get('recipient'),
        "subject": data.get('subject'),
        "body_plain": data.get('body-plain'),
        "timestamp": datetime.datetime.now().isoformat()
    }

    # Save to file (you can later use a real DB)
    with open('replies.json', 'a') as f:
        f.write(json.dumps(msg) + "\n")

    return jsonify({"status": "ok"}), 200 

@app.route("/unsubscribe", methods=["GET"])
def unsubscribe():
    email = request.args.get("email")
    if not email:
        return "Missing email", 400
    
    # Create an instance of UnSubscriber
    unsubscriber = UnSubscriber()
    # Remove the email from your Hubspot. 
    unsubscriber.unsubscribe(email)

    return f"{email} has been unsubscribed from future emails."

@app.route("/unsubscribe", methods=["POST"])
def unsubscribe_post():
    email = request.form.get("email")
    if not email:
        return "Missing email", 400
    
    # Create an instance of UnSubscriber
    unsubscriber = UnSubscriber()
    # Remove the email from your Hubspot. 
    unsubscriber.unsubscribe(email)

    return "", 204

@app.route('/mailgun/opened', methods=['POST'])
def mailgun_opened():
    data = request.form.to_dict()

    # Extract useful info
    timestamp = data.get("timestamp")
    recipient = data.get("recipient")

    # You can extract custom variables too:
    contact_email = data.get("v:contact_email", recipient)

    # Log to sheet
    sheet_utilizer = SpreadSheetUtils(sheet)
    row_index = sheet_utilizer.find_row_by_email(contact_email)
    if row_index:
        col_index = sheet_utilizer.get_col_index("Opened")
        sheet.update_cell(row_index, col_index, timestamp)

    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
