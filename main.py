from spotipy.oauth2 import SpotifyOAuth
import spotipy
import twilio.rest as twilio
import random
import logging
from configparser import ConfigParser

SPOTIFY_SCOPES = 'playlist-read-private playlist-modify-public playlist-modify-private'
HELLOS = ['Guten Morgen', 'Hello', 'Hola', 'Bonjour', 'Ahoi', 'Moin Moin', 'Servus', 'Good Morning']


class SendSpotifyLove:
    def __init__(self):
        config = ConfigParser()
        config.read('config.ini')

        self.spotify_user = config['SPOTIFY']['SPOTIFY_USER']
        self.spotipy_client_id = config['SPOTIFY']['SPOTIPY_CLIENT_ID']
        self.spotipy_client_secret = config['SPOTIFY']['SPOTIPY_CLIENT_SECRET']
        self.spotipy_redirect_uri = config['SPOTIFY']['SPOTIPY_REDIRECT_URI']
        self.spotify_user = config['SPOTIFY']['SPOTIFY_USER']
        self.source_playlist_id = config['SPOTIFY']['SOURCE_PLAYLIST_ID']
        self.target_playlist_id = config['SPOTIFY']['TARGET_PLAYLIST_ID']

        self.receiver_no = config['NUMBERS']['RECEIVER_NO']
        self.error_receiver_no = config['NUMBERS']['ERROR_RECEIVER_NO']
        self.sending_no = config['NUMBERS']['SENDING_NO']

        self.twilio_sid = config['TWILIO']['TWILIO_SID']
        self.twilio_token = config['TWILIO']['TWILIO_TOKEN']

        self.spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.spotipy_client_id,
                                                                        client_secret=self.spotipy_client_secret,
                                                                        redirect_uri=self.spotipy_redirect_uri,
                                                                        scope=SPOTIFY_SCOPES, cache_path='.sp_cache'))
        self.twilio_client = twilio.Client(self.twilio_sid, self.twilio_token)

        self.logger = logging.getLogger("SendSpotifyLove")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())

    def get_random_song_from_playlist(self):
        source_playlist = self.get_all_playlist_tracks(self.source_playlist_id)
        target_playlist = self.get_all_playlist_tracks(self.target_playlist_id)
        source_playlist_track_ids = [i['track']['id'] for i in source_playlist]
        target_playlist_track_ids = [i['track']['id'] for i in target_playlist]

        if len(source_playlist_track_ids) == 1:
            self.logger.warning("Sending last track of playlist. Quickly add another for tomorrow")
            text = "Sending last track of source playlist! Quickly add another before tomorrow morning."
            self.twilio_client.messages.create(from_=self.sending_no, body=text, to=self.error_receiver_no)

        track = random.choice(source_playlist)['track']
        return self.check_for_duplicate(track, target_playlist_track_ids)

    def get_all_playlist_tracks(self, playlist_id):
        results = self.spotify_client.playlist(playlist_id)['tracks']
        tracks = results['items']

        # Loops to ensure I get every track of the playlist
        while results['next']:
            results = self.spotify_client.next(results)
            tracks.extend(results['items'])
        return tracks

    def check_for_duplicate(self, new_track, playlist_tracks):
        if new_track['id'] in playlist_tracks:
            self.logger.info(f"Found duplicate track: {new_track['name']}. Removed and sending another.")
            text = f"{new_track['name']} has already been added to the playlist. Will be removed and another track sent."
            self.twilio_client.messages.create(from_=self.sending_no, body=text, to=self.error_receiver_no)
            self.spotify_client.user_playlist_remove_all_occurrences_of_tracks(self.spotify_user,
                                                                               self.source_playlist_id,
                                                                               [new_track['id']])
            return self.get_random_song_from_playlist()
        else:
            return new_track

    def move_track_to_target_playlist(self, track_id):
        self.spotify_client.user_playlist_add_tracks(self.spotify_user, self.target_playlist_id, [track_id])
        self.logger.info("Moved track to target playlist")
        self.spotify_client.user_playlist_remove_all_occurrences_of_tracks(self.spotify_user, self.source_playlist_id,
                                                                           [track_id])
        self.logger.info("Remove track from source playlist")

    def send_sms(self, track_url, track_name, artist_name):
        text = f"""
{random.choice(HELLOS)},
    
{artist_name} is playing "{track_name}" for you today.
{track_url}
        """
        self.twilio_client.messages.create(from_=self.sending_no, body=text, to=self.error_receiver_no)
        self.logger.info('Send sms')

    def run(self):
        try:
            track = self.get_random_song_from_playlist()
            self.logger.info(f"Chosen track: {track['name']} by {track['artists'][0]['name']}")
            self.send_sms(track['external_urls']['spotify'], track['name'], track['artists'][0]['name'])
            self.move_track_to_target_playlist(track['id'])
        except IndexError:
            self.logger.error("Source playlist is empty!")
            text = "Source playlist is empty!"
            self.twilio_client.messages.create(from_=self.sending_no, body=text, to=self.error_receiver_no)


def main(*args, **kwargs):
    SendSpotifyLove().run()
