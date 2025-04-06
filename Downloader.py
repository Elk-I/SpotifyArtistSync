import subprocess
import os
from SpotifyChecker import SpotifyChecker

class SpotifyPlaylistDownloader:
    def __init__(self, download_location="downloads"):
        # Set the default download location
        self.download_location = download_location

    def download_playlists(self, albums):
        # Ensure only one playlist is downloaded at a time
        for album in albums:
            print(f"Starting download for playlist: {album['name']}")
            self._download(album)
            print(f"Download completed for playlist: {album['name']}\n")
    
    def _download(self, album):
        playlist_url = album['external_urls']["spotify"]
        try:
            # Create a directory for the playlist in the main download location
            playlist_name = album['name']
            playlist_folder = os.path.join(self.download_location, playlist_name)
            os.makedirs(playlist_folder, exist_ok=True)
            
            # Use spotdl CLI to download the playlist and set the output to the folder for this playlist
            print(f"Downloading playlist to folder: {playlist_folder}")
            subprocess.run(['spotdl', playlist_url, '--output', playlist_folder], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading {playlist_url}: {e}")
        except FileNotFoundError:
            print("spotdl is not installed or not found in PATH. Please install spotdl.")
        except Exception as e:
            print(f"An unexpected error occurred while downloading {playlist_url}: {e}")


class SpotifyReleaseDownloader:
    def __init__(self, client_id, client_secret, download_location="downloads"):
        self.spotify_checker = SpotifyChecker(client_id, client_secret)
        self.downloader = SpotifyPlaylistDownloader(download_location)

    def download_new_releases(self, artist_name):
        # Get the list of albums by the artist
        print(f"Fetching albums for artist: {artist_name}")
        albums = self.spotify_checker.get_artist_albums(artist_name)
        
        # Check if the album has been downloaded already by checking the download directory
        undownloaded_albums = []
        for album in albums:
            album_folder = os.path.join(self.downloader.download_location, album['name'])
            if not os.path.exists(album_folder):
                print(f"Album '{album['name']}' not downloaded yet. Adding to the list.")
                undownloaded_albums.append(album)  # Use playlist URL or album URL

        # Download undownloaded albums
        if undownloaded_albums:
            print(f"Downloading {len(undownloaded_albums)} new albums...")
            self.downloader.download_playlists(undownloaded_albums)
        else:
            print("All albums are already downloaded.")