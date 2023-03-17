import argparse
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_credentials(key_file):
    creds = service_account.Credentials.from_service_account_file(
        key_file, scopes=["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    return creds

def get_user_groups(service, user_email):
    results = service.groups().list(userKey=user_email).execute()
    groups = results.get("groups", [])
    return groups

def get_rules(service, sheet_id):
    sheet_values = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Sheet1").execute()
    rows = sheet_values.get("values", [])
    rules = []
    for row in rows:
        rules.append((row[0], row[1], row[2]))
    return rules

def share_calendar(service, user_email, target_email, role):
    acl = {
        "role": role,
        "scope": {
            "type": "user",
            "value": target_email,
        },
    }
    try:
        service.calendarList().insert(calendarId=user_email, body=acl).execute()
    except HttpError as error:
        print(f"An error occurred: {error}")

def process_sharing_rules(credentials, user_email, rules_sheet_id):
    service = build("admin", "directory_v1", credentials=credentials)
    calendar_service = build("calendar", "v3", credentials=credentials)
    sheets_service = build("sheets", "v4", credentials=credentials)

    user_groups = get_user_groups(service, user_email)
    rules = get_rules(sheets_service, rules_sheet_id)

    for group in user_groups:
        for rule in rules:
            if group["email"] == rule[0]:
                share_calendar(calendar_service, user_email, rule[1], rule[2])

def main():
    parser = argparse.ArgumentParser(description="Google Workspace Automated Calendar Administration based on pre-set rules")
    parser.add_argument("--key-file", help="Path to the service account key file (in JSON format)", required=True)
    parser.add_argument("--user-email", help="Email address of the user to manage", required=True)
    parser.add_argument("--rules-sheet-id", help="ID of the Google Sheet containing the pre-set rules", required=True)

    args = parser.parse_args()

    credentials = get_credentials(args.key_file)
    process_sharing_rules(credentials, args.user_email, args.rules_sheet_id)

if __name__ == "__main__":
    main()
