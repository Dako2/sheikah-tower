import requests
from environment import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRETS

# Replace with your GitHub OAuth App credentials
CLIENT_ID = GITHUB_CLIENT_ID
CLIENT_SECRET = GITHUB_CLIENT_SECRETS
redirect_uri = "http://localhost"  # Usually, this can be set to "http://localhost"

# Step 1: Redirect the user to the GitHub OAuth authorization URL
auth_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={redirect_uri}&scope=public_repo"
print(f"Visit this URL to authorize: {auth_url}")

# Step 2: Get the authorization code from the redirected URL (manually)
authorization_code = input("Enter the authorization code from the URL: ")

# Step 3: Use the authorization code to obtain an access token
token_url = "https://github.com/login/oauth/access_token"
data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "code": authorization_code,
    "redirect_uri": redirect_uri,
}
response = requests.post(token_url, data=data, headers={"Accept": "application/json"})  # Explicitly request JSON response

if response.status_code == 200:
    response_data = response.json()
    if 'access_token' in response_data:
        access_token = response_data["access_token"]
        print(access_token)
    elif 'error' in response_data:
        print(f"Error: {response_data['error']}. Description: {response_data['error_description']}")
else:
    print(f"Failed to retrieve access token. HTTP status code: {response.status_code}")


"""
from flask import Flask, request, redirect, session, url_for
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a secret key for session

# GitHub OAuth Configuration
GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
REDIRECT_URI = 'http://your-server-ip/callback'  # Replace with your server's callback URL

@app.route('/auth')
def index():
    return 'Welcome to Your OAuth App'

@app.route('/auth/login')
def login():
    # Redirect the user to GitHub for authorization
    return redirect(f"{GITHUB_AUTHORIZE_URL}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=public_repo")

@app.route('/auth/callback')
def callback():
    # Handle the GitHub OAuth callback
    code = request.args.get('code')

    if code:
        # Exchange the authorization code for an access token
        response = requests.post(GITHUB_TOKEN_URL, {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI,
        })

        if response.status_code == 200:
            # Parse the JSON response to get the access token
            data = response.json()
            access_token = data['access_token']

            # Store the access token securely (e.g., in session)
            session['access_token'] = access_token

            # Redirect to a protected resource or your app's dashboard
            return redirect(url_for('dashboard'))
        else:
            return 'Failed to obtain access token'
    else:
        return 'Authorization code not received'

@app.route('/dashboard')
def dashboard():
    # Access GitHub resources using the stored access token
    access_token = session.get('access_token')

    if access_token:
        headers = {'Authorization': f'Bearer {access_token}'}
        # Make requests to GitHub API with the headers
        # Example: response = requests.get('https://api.github.com/user', headers=headers)
        # Process the response and display user data
        return 'GitHub user data here'

    return 'Access token not found'

if __name__ == '__main__':
    app.run(debug=True)


"""