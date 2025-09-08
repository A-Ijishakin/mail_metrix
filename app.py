from flask import Flask, request, jsonify
import json
import datetime

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

if __name__ == '__main__':
    app.run(debug=True)
