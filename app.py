from flask import Flask, redirect, request, session, url_for, render_template
import requests
import os
from apscheduler.schedulers.background import BackgroundScheduler
from utils.alert import reminder
from dotenv import load_dotenv
# import logging

# logging.basicConfig()
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTH_URL = 'https://auth.atlassian.com/authorize'
TOKEN_URL = 'https://auth.atlassian.com/oauth/token'
API_URL = 'https://api.atlassian.com/ex/jira/{cloud_id}/rest/agile/1.0'
REDIRECT_URI = 'http://localhost:5000/callback'

SCOPES = 'read:board-scope:jira-software read:project:jira read:jira-work read:issue-details:jira'

scheduler = BackgroundScheduler()

def fetch_boards_periodically():
    try:
        with app.app_context():
            access_token = session.get('access_token')
            if not access_token:
                print("No access token available. User needs to log in.")
                return

            cloud_response = requests.get(
                'https://api.atlassian.com/oauth/token/accessible-resources',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            cloud_data = cloud_response.json()
            if not cloud_data:
                print('No Jira sites found')
                return

            cloud_id = cloud_data[0]['id']
            boards_response = requests.get(
                f'{API_URL.replace("{cloud_id}", cloud_id)}/board',
                headers={'Authorization': f'Bearer {access_token}', "Accept": "application/json"}
            )
            boards_data = boards_response.json()

            if 'values' not in boards_data:
                print('No boards found')
                return

            boards = boards_data['values']
            user_issues = {}

            for board in boards:
                board_id = board['id']
                board_name = board['name']
                issues_response = requests.get(
                    f'{API_URL.replace("{cloud_id}", cloud_id)}/board/{board_id}/issue?jql=assignee=currentUser()',
                    headers={'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
                )
                issues_data = issues_response.json()
                user_issues[board_name] = [
                    {
                        'key': issue.get('key'),
                        'summary': issue.get('fields', {}).get('summary'),
                        'status': issue.get('fields', {}).get('status', {}).get('name'),
                        'duedate': issue.get('fields', {}).get('duedate')
                    }
                    for issue in issues_data.get('issues', [])
                ]
            reminder(user_issues,session['email'],int(session['days']))
    except Exception as e:
        print(f"An error occurred: {e}")

@app.route('/')
def home():
    return '<a href="/login">Log in with Jira</a>'

@app.route('/login')
def login():
    auth_request_url = (
        f"{AUTH_URL}?audience=api.atlassian.com&client_id={CLIENT_ID}&"
        f"scope={SCOPES}&redirect_uri={REDIRECT_URI}&response_type=code&prompt=consent"
    )
    return redirect(auth_request_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization failed', 400

    token_response = requests.post(
        TOKEN_URL,
        data={
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI,
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )

    token_data = token_response.json()
    access_token = token_data.get('access_token')

    if not access_token:
        return 'Failed to retrieve access token', 400

    session['access_token'] = access_token
    return redirect(url_for('configure'))

@app.route('/configure')
def configure():
    return render_template('index.html')

@app.route('/running', methods=['POST'])
def get_boards():
    session['email'] = request.form['email']
    session['days'] = request.form['days']
    temp = request.form['frequency']
    if temp=="daily":
        fetch_boards_periodically()
        scheduler.add_job(fetch_boards_periodically, 'interval',days=1)
        scheduler.start()
    elif temp=="weekly":
        fetch_boards_periodically()
        scheduler.add_job(fetch_boards_periodically, 'interval', days=7)
        scheduler.start()
    else:
        fetch_boards_periodically()
        scheduler.add_job(fetch_boards_periodically, 'interval', days = 30)
        scheduler.start()
    return '<p>The app is running</p>'

if __name__ == '__main__':
    try:
        app.run()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
