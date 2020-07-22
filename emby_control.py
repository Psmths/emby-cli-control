import requests
from requests.exceptions import HTTPError
import argparse
import json

#Dictionary to convert playlist name to item id, which you can find in the URL
#when viewing the playlist or item in Emby, i.e:
#http://192.168.1.131:8915/web/index.html#!/item?id=32102
#implies the playlist ID is 32102!
playlists = {
    "example": "31152"
}

#Your Emby API Key
apikey = ''

#The username you wish to control. Will be used to find the session ID.
userid = ""

#The target device player. For web playback this might be "Firefox"
device = 'Firefox'

#Emby server IP
address = ""
port = "8915"

parser = argparse.ArgumentParser()
parser.add_argument('command', help='The command you wish to run.')
parser.add_argument('--playlist', help='Shuffle a specified playlist.')
parser.add_argument('-v', help='Enable verbosity.', action='store_true')
args = parser.parse_args()

auth = {
    'api_key': apikey
}

content_header = {
    'accept': 'application/json'
}

commands_dict = {
    'pause': 'Pause',
    'resume': 'Unpause',
    'next': 'NextTrack',
    'previous': 'PreviousTrack'
}

#Get the session ID
try:
    response = requests.get('http://'+address+':'+port+'/Sessions', params=auth)
    response.raise_for_status()
    data = response.content
    session_data = json.loads(data)
    for session in session_data:
        sid = session['Id']
        uid = session['UserId']
        software = session['DeviceName']
        itemid = session['NowPlayingItem']['Id']
        if (args.v): print(sid+' => '+software)
        if ((uid == userid) and (software == device)):
            break

    if (args.v): print('Session key found! It is ' + sid)

except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')

#Parse command
if (args.command in commands_dict):
    if (args.v): print('Sending ' + commands_dict[args.command] + " command to " + sid)
    r = requests.post('http://'+address+':'+port+'/Sessions/'+sid+'/Playing/' + commands_dict[args.command], params=auth)

if (args.command == 'shuffle'):
    playlist_id = playlists[args.playlist]
    plparam = {
        'api_key': apikey,
        'PlayCommand': 'PlayShuffle',
        'ItemIds': playlists[args.playlist]
    }
    r = requests.post('http://'+address+':'+port+'/Sessions/'+sid+'/Playing', params=plparam)

if (args.command == 'similar'):
    playlist = []
    if (args.v): print('Finding something similar to ' + itemid + ' to play.')
    r = requests.get('http://'+address+':'+port+'/emby/Items/'+itemid+'/InstantMix', params=auth)
    for i in json.loads(r.content)['Items']:
        playlist.append(i["Id"])
    plparam = {
        'api_key': apikey,
        'PlayCommand': 'PlayShuffle',
        'ItemIds': ",".join(playlist)
    }
    r = requests.post('http://'+address+':'+port+'/Sessions/'+sid+'/Playing', params=plparam)
