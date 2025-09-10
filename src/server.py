import json
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from livekit.api.access_token import AccessToken
import datetime

logging.basicConfig(level=logging.DEBUG)
load_dotenv(".env.local")

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

app = Flask(__name__)
CORS(app)

@app.route("/token", methods=["POST"])
def token_endpoint():
    try:
        data = request.json or {}
        identity = data.get("participantName", "web-client")
        room_name = data.get("roomName", "sip-room")

        import jwt
        
        payload = {
            "iss": LIVEKIT_API_KEY,
            "name": identity,
            "sub": identity,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            "video": {
        "room": room_name,
        "roomJoin": True,
        "canPublish": True,
        "canSubscribe": True,
        "canPublishData": True
    },
    # metadata
        "metadata": json.dumps({
        "requested_agent": "aitema-universal-agent",
        "room": room_name
    })
}
        
        token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")
        return jsonify({"token": token})

    except Exception as e:
        logging.exception("Error generating token")
        return jsonify({"error": str(e)}), 500
    
@app.route("/disconnect-agent", methods=["POST"])
def disconnect_agent():
    try:
        data = request.json or {}
        agent_name = data.get("agentName", "persistent-agent")
        room_name = data.get("roomName", "sip-room")
        
       # DEBUG
        print(f"Disconnect request for agent: {agent_name} from room: {room_name}")
        
        return jsonify({"status": "disconnect_request_sent", "agent": agent_name})
        
    except Exception as e:
        logging.exception("Disconnect Error")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)