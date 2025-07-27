from flask import Blueprint, render_template, request, jsonify
from .openai_client import run_agent

bp = Blueprint('main', __name__)

@bp.route("/")
def home():
    return render_template("chat.html")

@bp.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    reply = run_agent(user_message)
    return jsonify({"reply": reply})