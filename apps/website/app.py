import os

import requests
from flask import Flask, request
from dotenv import load_dotenv; load_dotenv()

from blueprints.gmail.gmail import gmail_bp
from blueprints.discord.discord import discord_bp

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('flask_secret_key')

app.register_blueprint(gmail_bp)
app.register_blueprint(discord_bp)


@app.route('/test-pub-sub', methods=['GET', 'POST'])
def test_pub_sub():
    print(request.get_data().decode())
    # print(request.get_json())

    requests.post(
        'https://heath-innovation-stickers-sounds.trycloudflare.com',
        headers=dict(request.headers),
        data=request.get_json()
    )
    return {'success': True}


if __name__ == "__main__":
    app.run(host="0.0.0.0")
