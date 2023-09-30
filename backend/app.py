from flask import Flask, jsonify
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
# Load environment variables
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
# Set up Spotipy client credentials
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

@app.route('/')
def index():
    return "Welcome to the Music Cooker!"

@app.route('/artist/<name>')
def get_artist(name):
    results = sp.search(q='artist:' + name, type='artist')
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
