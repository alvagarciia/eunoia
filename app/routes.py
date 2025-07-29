from flask import Blueprint, render_template, request, jsonify
from .openai_client import run_agent

bp = Blueprint('main', __name__)

@bp.route("/")
def home():
    return render_template("chat.html")

@bp.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    session_id = request.json.get("session_id")
    
    # Fallback to a default if session_id is missing
    if not session_id:
        session_id = "default_session"
    
    reply = run_agent(user_message, session_id)
    return jsonify({"reply": reply})