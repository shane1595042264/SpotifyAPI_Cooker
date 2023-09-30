from flask import render_template, jsonify, request, redirect, url_for
import os
import spotipy
import plotly
import plotly.graph_objs as go
import json
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

# Set up Spotipy client credentials
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def setup_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            artist_name = request.form['artist_name']
            return redirect(url_for('get_artist', name=artist_name))
        return render_template('index.html')


    @app.route('/artist/<name>')
    def get_artist(name):
        # Fetch artist information
        artist_search = sp.search(q='artist:' + name, type='artist')
        artist_name = artist_search['artists']['items'][0]['name']
        artist_id = artist_search['artists']['items'][0]['id']
        
        # Fetch the artist's top tracks
        top_tracks = sp.artist_top_tracks(artist_id, country='US')
        tracks = [track['name'] for track in top_tracks['tracks']]
        popularity = [track['popularity'] for track in top_tracks['tracks']]
        
        # Create a bar chart using Plotly for the top tracks
        data = [
            go.Bar(
                x=tracks,
                y=popularity
            )
        ]
        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Fetch audio features for the top tracks
        track_ids = [track['id'] for track in top_tracks['tracks']]
        audio_features = sp.audio_features(track_ids)
        
        # Extract average features for the radar chart
        features_for_display = ['danceability', 'energy', 'acousticness', 'valence', 'instrumentalness']
        avg_features = {feature: sum([track[feature] for track in audio_features]) / len(audio_features) for feature in features_for_display}

        # Create the radar chart
        data = [go.Scatterpolar(
            r = list(avg_features.values()),
            theta = list(avg_features.keys()),
            fill = 'toself'
        )]

        radarJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

        # Fetch genres associated with the artist
        genres = artist_search['artists']['items'][0]['genres']
        
        # Count genre occurrences (you can also use a database or cache to store and update this information)
        genre_counts = {}
        for genre in genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

        # Create the pie chart
        genre_data = [go.Pie(
            labels = list(genre_counts.keys()),
            values = list(genre_counts.values())
        )]

        genreJSON = json.dumps(genre_data, cls=plotly.utils.PlotlyJSONEncoder)

        tracks = sp.search(q='artist:' + name, type='track', limit=50)
        popularities = [track['popularity'] for track in tracks['tracks']['items']]

        # Create the histogram for popularity distribution
        popularity_data = [go.Histogram(
            x=popularities
        )]

        popularityJSON = json.dumps(popularity_data, cls=plotly.utils.PlotlyJSONEncoder)

            # Fetch collaborating artists
        collaborating_artists = []
        for track in top_tracks['tracks']:
            for artist in track['artists']:
                if artist['name'] != name:  # Exclude the main artist
                    collaborating_artists.append(artist['name'])
        
        # We'll create a basic data structure for the collaboration network
        # Nodes represent artists, and edges represent collaborations
        nodes = [{"id": name, "label": name}]  # Start with the main artist
        edges = []
        for collaborator in set(collaborating_artists):  # Using set to remove duplicates
            nodes.append({"id": collaborator, "label": collaborator})
            edges.append({"from": name, "to": collaborator})

        # This is a basic implementation. A more refined version would consider multiple collaborations and weight edges accordingly.
        network_data = {"nodes": nodes, "edges": edges}
        networkJSON = json.dumps(network_data)

        # Extract valence and energy for the mood map
        valence = [feature['valence'] for feature in audio_features]
        energy = [feature['energy'] for feature in audio_features]
        track_names = [track['name'] for track in top_tracks['tracks']]
        
        # Create the scatter plot for the mood map
        mood_data = [go.Scatter(
            x = energy,
            y = valence,
            mode = 'markers+text',
            text = track_names,
            textposition = 'top center'
        )]

        moodJSON = json.dumps(mood_data, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('artist.html', artist_name=artist_name, graphJSON=graphJSON, radarJSON=radarJSON, genreJSON=genreJSON, popularityJSON=popularityJSON, networkJSON=networkJSON, moodJSON=moodJSON)

