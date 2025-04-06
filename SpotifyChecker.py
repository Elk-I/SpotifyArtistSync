import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyChecker:
    def __init__(self, client_id, client_secret):
        # Authenticate with Spotify using the client credentials
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
    
    def get_artist_albums(self, artist_name, limit=50):
        # Search for the artist
        results = self.sp.search(q=artist_name, type='artist', limit=1)
        if not results['artists']['items']:
            print(f"Artist '{artist_name}' not found.")
            return

        # Get the artist's ID
        artist_id = results['artists']['items'][0]['id']
        
        # Get the albums of the artist
        albums = self.sp.artist_albums(artist_id, limit=limit)  # Limit to 50 albums, you can adjust this
        return albums["items"]
