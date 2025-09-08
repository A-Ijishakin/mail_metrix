from flask import Flask, request, jsonify
import json
import datetime
from unsubscribe import UnSubscriber

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

if __name__ == '__main__':
    app.run(debug=True)
