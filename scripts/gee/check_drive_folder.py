import json
import urllib.request
import urllib.parse
from pathlib import Path
from ee import oauth

def get_token():
    cred_file = Path.home() / '.config' / 'earthengine' / 'credentials'
    with open(cred_file, 'r') as f:
        creds = json.load(f)
    data = urllib.parse.urlencode({
        'client_id': oauth.CLIENT_ID,
        'client_secret': oauth.CLIENT_SECRET,
        'refresh_token': creds['refresh_token'],
        'grant_type': 'refresh_token'
    }).encode()
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())['access_token']

def check_folder():
    t = get_token()
    folder_id = '1Sb-0SAZU0dyor_2w-yzz55ATddgXttFO'
    q = f"'{folder_id}' in parents and trashed = false"
    url = f"https://www.googleapis.com/drive/v3/files?q={urllib.parse.quote(q)}&fields=files(id,name,size,mimeType)"
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {t}'})
    with urllib.request.urlopen(req) as resp:
        items = json.loads(resp.read().decode()).get('files', [])
    print(f"Items in LowerGodavari_Floods_2022: {len(items)}")
    for item in items:
        sz = int(item.get('size', 0)) / (1024*1024)
        print(f"  - {item['name']} ({sz:.2f} MB)")

if __name__ == '__main__':
    check_folder()
