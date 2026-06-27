import requests
import os
from datetime import datetime, timezone

TOKEN = os.getenv("MADI_PAT")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# 🔧 Cutoff date (UTC)
CUTOFF_DATE_STR = "2026-06-20"
CUTOFF_DATE = datetime.strptime(CUTOFF_DATE_STR, "%Y-%m-%d").replace(tzinfo=timezone.utc)

BASE_URL = "https://api.github.com/user/repository_invitations"

all_invites = []
page = 1
per_page = 100

print("Fetching all invitations with pagination...")

while True:
    url = f"{BASE_URL}?per_page={per_page}&page={page}"
    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        print("Failed to fetch invitations:", resp.text)
        exit(1)

    invites = resp.json()

    if not invites:
        break

    print(f"Fetched page {page} with {len(invites)} invites")
    all_invites.extend(invites)
    page += 1

print(f"\nTotal invitations fetched: {len(all_invites)}")

if not invites:
    print("No pending invitations.")
    exit(0)

accepted_count = 0
skipped_count = 0

for invite in invites:
    repo_name = invite["repository"]["full_name"]
    invitation_id = invite["id"]
    created_at_str = invite["created_at"]

    # Convert API timestamp → datetime
    created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

    # 🔍 Apply filter
    if created_at < CUTOFF_DATE:
        print(f"Skipped (old): {repo_name} | Created at: {created_at_str}")
        skipped_count += 1
        continue

    # Accept invitation
    accept_url = f"https://api.github.com/user/repository_invitations/{invitation_id}"
    r = requests.patch(accept_url, headers=headers)

    if r.status_code == 204:
        print(f"Accepted: {repo_name} | Created at: {created_at_str}")
        accepted_count += 1
    else:
        print(f"Failed: {repo_name} → {r.text}")

print("\nSummary:")
print(f"Accepted: {accepted_count}")
print(f"Skipped (old): {skipped_count}")
