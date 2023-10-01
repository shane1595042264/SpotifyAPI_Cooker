from flask import render_template, jsonify, request, redirect, url_for
import os
import spotipy
import plotly
import plotly.graph_objs as go
import json
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import random
from collections import Counter
import re
import string
from flask import Flask, redirect, request, session, url_for
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter
import datetime

load_dotenv()

# Set up Spotipy client credentials
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="http://127.0.0.1:5000/callback",
    scope="user-library-read user-read-recently-played user-top-read" 
)

def setup_routes(app):
    @app.route('/login')
    def login():
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    @app.route('/callback')
    def callback():
        token_info = sp_oauth.get_access_token(request.args['code'])
        session['token_info'] = token_info
        return redirect(url_for('user_stats'))
    @app.route('/user_stats')
    def user_stats():
        token_info = session.get('token_info', None)
        if not token_info:
            return redirect(url_for('login'))
        
        token = token_info['access_token']
        sp = spotipy.Spotify(auth=token)
        
        # Fetch the last 50 tracks played by the user
        recent_tracks = sp.current_user_recently_played(limit=50)

        # Extract the day of the week for each track played
        days_played = [datetime.datetime.fromisoformat(track['played_at'].rstrip('Z')).strftime('%A') for track in recent_tracks['items']]
        
        top_tracks = sp.current_user_top_tracks(limit=1, time_range='long_term')
        most_replayed_track_image = top_tracks['items'][0]['album']['images'][0]['url'] if top_tracks['items'] and top_tracks['items'][0]['album']['images'] else None

        most_replayed_track = top_tracks['items'][0]['name'] if top_tracks['items'] else "No data available"
        # Count occurrences of each day
        day_counts = Counter(days_played)

        # Determine the most active day
        most_active_day = day_counts.most_common(1)[0][0]

        # Render the user stats page with the gathered data
        return render_template('user_stats.html', most_active_day=most_active_day, most_replayed_track=most_replayed_track, most_replayed_track_image=most_replayed_track_image)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
                artist_name = request.form['artist_name']
                return redirect(url_for('get_artist', name=artist_name))
            
            # Fetch recommended artists
        recommended_artists = fetch_recommended_artists()
        
        return render_template('index.html', recommended_artists=recommended_artists)


    @app.route('/artist/<name>')
    def get_artist(name):
        # Fetch artist information
        artist_search = sp.search(q='artist:' + name, type='artist')
        artist_name = artist_search['artists']['items'][0]['name']
        artist_id = artist_search['artists']['items'][0]['id']
        image_url = artist_search['artists']['items'][0]['images'][0]['url'] if artist_search['artists']['items'][0]['images'] else None

        # Fetch the artist's top tracks
        top_tracks = sp.artist_top_tracks(artist_id, country='US')
        tracks = [track['name'] for track in top_tracks['tracks']]
        popularity = [track['popularity'] for track in top_tracks['tracks']]
        
        # Create a bar chart
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
        
        # Count genre occurrences 
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

        # Nodes represent artists, and edges represent collaborations
        nodes = [{"id": name, "label": name}]  # Start with the main artist
        edges = []
        for collaborator in set(collaborating_artists):  # Using set to remove duplicates
            nodes.append({"id": collaborator, "label": collaborator})
            edges.append({"from": name, "to": collaborator})

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

        return render_template('artist.html', artist_name=artist_name, graphJSON=graphJSON, radarJSON=radarJSON, genreJSON=genreJSON, popularityJSON=popularityJSON, networkJSON=networkJSON, moodJSON=moodJSON, image_url=image_url)

    def fetch_recommended_artists():
        # Fetch popular playlists
        playlists = sp.category_playlists(category_id='pop', limit=5)
        playlist_ids = [playlist['id'] for playlist in playlists['playlists']['items']]
        
        # Extract tracks from these playlists and get artist details
        all_artists = []
        for playlist_id in playlist_ids:
            tracks = sp.playlist_tracks(playlist_id)
            for item in tracks['items']:
                all_artists.extend(item['track']['artists'])
        
        # Randomly select a few artists to display
        selected_artist_ids = random.sample([artist['id'] for artist in all_artists], 5)  # Select 5 random artist IDs

        # Fetch detailed artist information based on the IDs
        detailed_artists = sp.artists(selected_artist_ids)['artists']
        
        return detailed_artists
    @app.route('/top_tracks_by_year')
    def top_tracks_by_year():
        return render_template('yearly_top_tracks.html')
    @app.route('/get_yearly_data/<int:year>')
    def get_yearly_data(year):
        market = 'US'
        
        # Fetch top tracks from Spotify API based on the year
        results = sp.search(q=f'year:{year}', type='track', limit=50, market=market)
        tracks = results['tracks']['items']

        # Sort tracks by popularity and take top 10
        tracks = sorted(tracks, key=lambda x: -x['popularity'])[:10]

        popularity = [track['popularity'] for track in tracks]
        track_names = [track['name'] for track in tracks]

        # Retrieve image URLs for the tracks
        image_urls = [track['album']['images'][0]['url'] if track['album']['images'] else None for track in tracks]
        audio_urls = [track['preview_url'] for track in tracks]  # Extracting the preview_url
        artists = [track['artists'][0]['name'] for track in tracks]

        data = {
            'type': 'bar',
            'y': artists,
            'x': popularity,
            'text': track_names,
            'orientation': 'h',
            'images': image_urls,
            'audio_urls': audio_urls  # Adding the audio URLs to the data
        }

        return jsonify(data)



