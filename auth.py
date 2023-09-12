import requests
from environment import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRETS

# Replace with your GitHub OAuth App credentials
client_id = GITHUB_CLIENT_ID
client_secret = GITHUB_CLIENT_SECRETS
redirect_uri = "http://34.136.140.65"  # Usually, this can be set to "http://localhost"

# Step 1: Redirect the user to the GitHub OAuth authorization URL
auth_url = 
f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=public_repo"
print(f"Visit this URL to authorize: {auth_url}")

# Step 2: Get the authorization code from the redirected URL (manually)
authorization_code = input("Enter the authorization code from the URL: ")

# Step 3: Use the authorization code to obtain an access token
token_url = "https://github.com/login/oauth/access_token"
data = {
    "client_id": client_id,
    "client_secret": client_secret,
    "code": authorization_code,
    "redirect_uri": redirect_uri,
}
response = requests.post(token_url, data=data)
access_token = response.json()["access_token"]

# Now you can use the access token for API requests to GitHub.

