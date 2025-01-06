from flask import Flask, redirect, request, session, url_for
import requests
import json
import base64
from dotenv import load_dotenv
import os

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
    return redirect(url_for('get_boards'))

@app.route('/get_boards')
def get_boards():
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('login'))

    cloud_response = requests.get(
        'https://api.atlassian.com/oauth/token/accessible-resources',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    cloud_data = cloud_response.json()      
    if not cloud_data:
        return 'No Jira sites found', 404

    cloud_id = cloud_data[0]['id']  
    # print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
    # Fetch boards from the Jira API
    boards_response = requests.get(
        f'{API_URL.replace("{cloud_id}", cloud_id)}/board',
        headers={'Authorization': f'Bearer {access_token}',
                 "Accept": "application/json",}
    )
    boards_data = boards_response.json()
    
    if 'values' not in boards_data:
        return 'No boards found', 404

    boards = boards_data['values']
    user_issues = {}

    # Iterate over boards to fetch issues assigned to the current user
    for board in boards:
        board_id = board['id']
        board_name = board['name']

        # Fetch issues for the board assigned to the current user
        issues_response = requests.get(
            f'{API_URL.replace("{cloud_id}", cloud_id)}/board/{board_id}/issue?jql=assignee=currentUser()',
            headers={'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}
        )
        issues_data = issues_response.json()
        user_issues[board_name] = [
        {   
        'key': issue.get('key'),
        'summary': issue.get('fields', {}).get('summary'),
        'status': issue.get('fields', {}).get('status', {}).get('name')
        }
        for issue in issues_data.get('issues', [])
        ]

    # Display the boards and assigned issues
    return json.dumps(user_issues, indent=4)
# def decode_jwt(token):
#     # Split the token into its parts
#     header, payload, signature = token.split('.')
    
#     # Decode the payload (second part of the token)
#     padded_payload = payload + '=' * (4 - len(payload) % 4)  # Add padding if necessary
#     decoded_bytes = base64.urlsafe_b64decode(padded_payload)
#     decoded_payload = json.loads(decoded_bytes)
    
#     return decoded_payload



if __name__ == '__main__':
    app.run()
