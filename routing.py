from flask import Blueprint, render_template, request, jsonify
from processor import process_data

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")  # use your index.html

@main.route("/generate", methods=["POST"])
def generate():
    data = request.json
    result = process_data(data)
    return jsonify(result)