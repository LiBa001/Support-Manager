import requests
import os

BOT_TOKEN = "BOT-TOKEN"
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')


"""class User:
    def __init__(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token

        data = self.get()
        self._name = data['username']
        self._discriminator = data['discriminator']
        self._id = data['id']
        self._avatar = data['avatar']

    @staticmethod
    def oauth(**data):
        data['client_id'] = CLIENT_ID
        data['client_secret'] = CLIENT_SECRET
        data['redirect_uri'] = REDIRECT_URI

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post('%s/oauth2/token' % API_ENDPOINT, data, headers)
        r.raise_for_status()
        return r.json()

    def exchange_code(self, code):
        data = self.oauth(code=code, grant_type='authorization_code')
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']

        return self.access_token

    def refresh_access_token(self, refresh_token):
        data = self.oauth(refresh_token=refresh_token, grant_type='refresh_token')
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']

        return self.access_token

    def get(self, path: str=""):
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        r = requests.get(API_ENDPOINT + "/users/@me" + path, headers=headers)
        r.raise_for_status()
        return r.json()

    @property
    def servers(self):
        return self.get('/guilds')

    @property
    def info(self):
        return self.get()

    @property
    def id(self):
        return self.info['id']

    @property
    def avatar_url(self):
        url = f"https://cdn.discordapp.com/avatars/{self.id}/{self._avatar}.png"
        return url"""


class Client:
    def __init__(self, token):
        self.token = token

    def get(self, path):
        headers = {
            'Authorization': f'Bot {self.token}'
        }
        r = requests.get(API_BASE_URL + path, headers=headers)
        r.raise_for_status()
        return r.json()

    def get_server(self, server_id: str):
        return self.get('/guilds/' + server_id)

    @property
    def servers(self):
        return self.get('/users/@me/guilds')

    def get_user(self, user_id: str):
        return self.get('/users/' + user_id)


client = Client(token=BOT_TOKEN)
