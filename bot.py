import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application

# 1. Setup Flask
app = Flask(__name__)

# 2. Setup Bot
TOKEN = os.getenv("TOKEN")
# Note: Use a proper webhook setup here if you're not using Polling
application = Application.builder().token(TOKEN).build()

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

# This is what Gunicorn looks for (bot:app)
if __name__ == "__main__":
    # Your local testing logic
    pass
