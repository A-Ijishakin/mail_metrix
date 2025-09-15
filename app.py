from dataclasses import dataclass
import re 
from flask import Flask, request, jsonify
import gspread
import json
import datetime
from unsubscribe import UnSubscriber
from oauth2client.service_account import ServiceAccountCredentials
from spread_sheet_utils import SpreadSheetUtils
from flask import render_template

# Setup Google Sheets client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Load the credentials from environment variable
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Email Mastersheet").sheet1  # Adjust as needed

app = Flask(__name__)

# This stores replies into a local JSON file
@app.route('/mailgun/inbound', methods=['POST'])
def receive_reply():
    data = request.form.to_dict()

    unique_id = data.get("recipient-variables", {}).get("unique_id")
    if not unique_id:
        # fallback: maybe parse the original message ID or use subject matching
        return "Unique ID not found in metadata", 400

    date_received = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Update Google Sheet
    sheet_utilizer = SpreadSheetUtils(sheet)
    row_index = sheet_utilizer.find_row_by_col_value("ID", unique_id)

    if row_index:
        reply_col_index = sheet_utilizer.get_col_index("Reply Date")
        sheet.update_cell(row_index, reply_col_index, date_received)
        return "OK", 200
    else:
        return "ID not found", 404
     
@app.route("/unsubscribe", methods=["GET"])
def unsubscribe():
    email = request.args.get("email")

    if not email:
        return "Missing email", 400
    
    # Create an instance of UnSubscriber
    unsubscriber = UnSubscriber()
    # Remove the email from your Hubspot. 
    unsubscriber.unsubscribe(email)

    #update the google sheet to reflect the unsubscribed status.
    unique_id = request.args.get("unique_id")
    sheet_utilizer = SpreadSheetUtils(sheet)

    # Find the row index where ID column matches the unique_id
    row_index = sheet_utilizer.find_row_by_col_value("ID", unique_id) 
    
    if row_index:
        unsub_col_index = sheet_utilizer.get_col_index("Unsubscribed")
        sheet.update_cell(row_index, unsub_col_index, "1")
        return render_template("unsubscribed.html")
    else:
        return "ID not found", 404

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
    row_index = sheet_utilizer.find_row_by_col_value('Email',contact_email)
    if row_index:
        col_index = sheet_utilizer.get_col_index("Opened")
        sheet.update_cell(row_index, col_index, timestamp)

    return "OK", 200

@app.route('/mailgun/bounced', methods=['POST'])
def mailgun_bounced():
    data = request.form.to_dict()

    # Custom vars, if you used any
    unique_id = data.get("v:unique_id", "84930")

    sheet_utilizer = SpreadSheetUtils(sheet)

    # Find the row index where ID column matches the unique_id
    row_index = sheet_utilizer.find_row_by_col_value("ID", unique_id)
    
    if row_index:
        bounced_col_index = sheet_utilizer.get_col_index("Bounced")
        sheet.update_cell(row_index, bounced_col_index, "1")
        return f"Email bounced to individual at {unique_id}.", 200

    else:
        return "ID not found", 404

if __name__ == '__main__':
    app.run(debug=True)

