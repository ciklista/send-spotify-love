# Send Spotify Love :notes: :green_heart:
Small amd simple python script to send spotify track links via SMS (yes, this still exists). 

The script chooses a random track form a source playlist, sends the link via SMS and drops the track to a target 
playlist. The track will be removed from the source playlist. The script also sends warnings if the source playlist is 
(almost) emtpy or if tracks are already present in the source playlist.

Build with the [spotipy](https://spotipy.readthedocs.io/en/2.13.0/) and [twilio](https://www.twilio.com/docs/sms) client libraries.

*Alternatively, you could write a [telegram bot](https://core.telegram.org/bots/api), or anything else that is more 
trendy then SMS, that does the job. Feel free to reach out if you want to contribute.*

## Getting Started
### Prerequisite
- A Spotify developers account and a Spotify app. Check the 
[Spotify documentation](https://developer.spotify.com/documentation/web-api/quick-start/) for further instructions. Also
refer to the [section](#note-on-the-spotify-authentication) below.
- A Twilio account. Refer to the 
[Twilio documenation](https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account) 
for information on how to get a free trial account.
- An environment where the script can run periodically. Could be deployed as a 
[Google Cloud Function](https://cloud.google.com/functions/docs/quickstart-python) or 
[AWS lambda](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html) and triggered from a cron-like service 
(e.g. [Google Cloud Scheduler](https://rominirani.com/google-cloud-functions-tutorial-using-the-cloud-scheduler-to-trigger-your-functions-756160a95c43#:~:text=The%20Cloud%20Scheduler%20now%20available,mechanisms%20that%20you%20can%20configure.)).

### Setup 
Fill out all necessary configuration in the ``config.ini`` file. Phone numbers must be provided in 
[E.164](https://www.twilio.com/docs/glossary/what-e164) format. Call the ```main()``` function and start sending 
[great music](https://open.spotify.com/playlist/3MGILGIMK6mgJZvvmDI4Kg?si=Q_O_0evkQlGN8ijkSYyQcA).

### Note on the Spotify authentication

*Short*: set a random redirect URI (like ``https://localhost:8080``) when setting up your Spotify App. When you run the 
script for the first time make sure to run it on a system that has a browser. Copy the link you are being 
redirected to to the console to create a cache file that holds your OAuth token. Future runs will work with that cache file.

*Long*: As the script is requesting user specific data, we need to go through a **User Authorization** flow (basically, we need
to log into our Spotify account, get a token, store that somewhere. That token is then used to make the requests.). 
The basic principle behind this is [OAuth](https://oauth.net/articles/authentication/). This process includes a callback
URI that it can call and sent the token to once you have successfully logged into the service. For the purpose of this 
script, you can set the callback URI in your Spotify app to any URI (like ``https://localhost:8080``). Make sure that 
the URI in ``config.ini`` matches your URI in the Spotify app settings.

Find out more on the Spotify authorization [here](https://developer.spotify.com/documentation/general/guides/authorization-guide/).

When you run the script for the first time, the spotipy library will try to open a browser (make sure that you are 
running the script somewhere where there is a browser) and will walk you through the Spotify login process. Once done,
don't get distracted by the error page, simply copy the link that your browser has tried to open to the python console
and hit enter. The spotipy library will store the relevant tokens in the ``.sp_cache`` file. The script will automatically 
use the tokens from that cache file from now on (make sure to pass that cache file to your 
target environment).
