import os
import json
from flask import Flask, request, jsonify, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from Downloader import SpotifyReleaseDownloader

app = Flask(__name__)
ARTIST_FILE = os.environ.get('ARTIST_FILE', 'artists.json')
# Get download location from environment variable or use default
DOWNLOAD_LOCATION = os.environ.get('DOWNLOAD_LOCATION', 'downloads')


# --- Artist Storage ---

def load_artists():
    if not os.path.exists(ARTIST_FILE):
        # Ensure directory exists
        os.makedirs(os.path.dirname(ARTIST_FILE), exist_ok=True)
        return set()
    with open(ARTIST_FILE, 'r') as f:
        try:
            return set(json.load(f))
        except json.JSONDecodeError:
            return set()

def save_artists():
    with open(ARTIST_FILE, 'w') as f:
        json.dump(sorted(list(artists)), f, indent=2)


artists = load_artists()


# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html', download_dir=DOWNLOAD_LOCATION)

@app.route('/artists', methods=['GET'])
def get_artists():
    return jsonify(sorted(artists)), 200

@app.route('/artists', methods=['POST'])
def add_artist():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Artist name is required'}), 400
    artists.add(name.strip())
    save_artists()
    return jsonify({'message': f'Artist "{name}" added.'}), 201

@app.route('/artists', methods=['DELETE'])
def remove_artist():
    data = request.get_json()
    name = data.get('name')
    if name in artists:
        artists.remove(name)
        save_artists()
        return jsonify({'message': f'Artist "{name}" removed.'}), 200
    return jsonify({'error': f'Artist "{name}" not found.'}), 404

@app.route('/download', methods=['POST'])
def trigger_download():
    data = request.get_json()
    name = data.get('name')

    # Get credentials from environment or use defaults
    client_id = os.environ.get('SPOTIFY_CLIENT_ID', 'a411e45c65ee4ef0810647fc57d5fbdd')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET', '4635e21cf91d4b318f39a7dd1a2a638e')
    release_downloader = SpotifyReleaseDownloader(client_id, client_secret, DOWNLOAD_LOCATION)

    if name:
        if name not in artists:
            return jsonify({'error': 'Artist not found'}), 404
        try:
            release_downloader.download_new_releases(name)
            return jsonify({'message': f'Releases downloaded for "{name}".'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        results = {}
        for artist in artists:
            try:
                release_downloader.download_new_releases(artist)
                results[artist] = "Success"
            except Exception as e:
                results[artist] = f"Error: {str(e)}"
        return jsonify(results), 200


# --- Background Job ---

def run_release_downloader():
    client_id = os.environ.get('SPOTIFY_CLIENT_ID', 'a411e45c65ee4ef0810647fc57d5fbdd')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET', '4635e21cf91d4b318f39a7dd1a2a638e')
    release_downloader = SpotifyReleaseDownloader(client_id, client_secret, DOWNLOAD_LOCATION)
    for artist in artists:
        try:
            release_downloader.download_new_releases(artist)
            print(f"Checked releases for {artist}")
        except Exception as e:
            print(f"Error checking releases for {artist}: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(run_release_downloader, 'interval', hours=1)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


# --- Run App ---

if __name__ == '__main__':
    # Make sure download directory exists
    os.makedirs(DOWNLOAD_LOCATION, exist_ok=True)
    print(f"Download location set to: {DOWNLOAD_LOCATION}")
    
    # In Docker, we should listen on 0.0.0.0
    app.run(host='0.0.0.0', port=5000)