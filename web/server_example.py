import os
from flask import Flask, g, session, redirect, request, url_for, render_template
from requests_oauthlib import OAuth2Session
import sqlib
from web import api_handler
import json

OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
OAUTH2_REDIRECT_URI = 'http://192.168.178.113:5000/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


@app.route('/')
def index():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    return render_template('index.html', user=user)


@app.route('/login')
def login():
    scope = request.args.get(
        'scope',
        'identify guilds')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token
    return redirect(url_for('.me'))


@app.route('/me')
def me():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    bot_guilds_ids = [s['id'] for s in api_handler.client.servers]

    guilds = [g for g in guilds if g['id'] in bot_guilds_ids]

    return render_template("user.html", user=user, guilds=guilds)


@app.route('/servers/<string:server_id>')
def server(server_id):
    oauth2_token = session.get('oauth2_token')

    if oauth2_token is None:
        return redirect(url_for('.login'))

    discord = make_session(token=oauth2_token)
    user = discord.get(API_BASE_URL + '/users/@me').json()
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    bot_guilds_ids = [s['id'] for s in api_handler.client.servers]

    try:
        guild = next(item for item in guilds if item['id'] == server_id and item['id'] in bot_guilds_ids)
    except StopIteration:
        guild = None

    tickets = sqlib.tickets.get_all()
    tickets = list(filter(lambda t: t[5] == 0, tickets))
    tickets = list(filter(lambda t: t[2] == server_id, tickets))

    authors = {}
    author_id = None
    for ticket in tickets:
        if not author_id == ticket[1]:
            author_id = ticket[1]
            authors[author_id] = api_handler.client.get_user(author_id)

    return render_template("server.html", user=user, server=guild, tickets=tickets, authors=authors, to_json=json.loads)


@app.route('/contact')
def contact():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    return render_template('contact.html', user=user)


@app.errorhandler(404)
def not_found(error):
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    return render_template('404.html', user=user), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0')
