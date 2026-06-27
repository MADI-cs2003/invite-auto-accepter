import requests
import os

TOKEN = os.getenv("MADI_PAT")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Fetch pending invitations
resp = requests.get(
    "https://api.github.com/user/repository_invitations",
    headers=headers
)

if resp.status_code != 200:
    print("Failed to fetch invitations:", resp.text)
    exit(1)

invites = resp.json()

if not invites:
    print("No pending invitations.")
else:
    print(f"Found {len(invites)} invitations.")

# Accept each invitation
for invite in invites:
    repo_name = invite["repository"]["full_name"]
    invitation_id = invite["id"]

    accept_url = f"https://api.github.com/user/repository_invitations/{invitation_id}"
    r = requests.patch(accept_url, headers=headers)

    if r.status_code == 204:
        print(f"Accepted: {repo_name}")
    else:
        print(f"Failed: {repo_name} → {r.text}")
