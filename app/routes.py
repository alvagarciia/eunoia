from flask import Blueprint, render_template, request, jsonify
from .openai_client import get_openai_response

bp = Blueprint('main', __name__)

@bp.route("/")
def home():
    return render_template("chat.html")

@bp.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    reply = get_openai_response(user_message)
    return jsonify({"reply": reply})