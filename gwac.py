import argparse
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from termcolor import colored, cprint
from tabulate import tabulate
import configparser

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.group.readonly",
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

def get_credentials(key_file, subject, scopes=SCOPES):
    creds = service_account.Credentials.from_service_account_file(
        key_file
    ).with_subject(subject).with_scopes(scopes)
    return creds

def get_user_groups(service, user_email):
    results = service.groups().list(userKey=user_email).execute()
    groups = results.get("groups", [])
    return groups

def get_rules(service, sheet_id, sheet_range):
    sheet_values = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=sheet_range).execute()
    rows = sheet_values.get("values", [])
    rules = []
    for row in rows:
        rules.append((row[0], row[1], row[2]))
    return rules

def share_calendar(service, user_email, target_email, role, target_type="group"):
    try:
        # Get the ACL of the user_email's calendar
        acl_list = service.acl().list(calendarId=user_email).execute()
        items = acl_list.get("items", [])

        # Check if the target_email (group) already has access
        existing_calendar_entry = None
        for acl_entry in items:
            scope_type = acl_entry.get("scope", {}).get("type")
            scope_value = acl_entry.get("scope", {}).get("value")

            if scope_type == target_type and scope_value == target_email:
                existing_calendar_entry = acl_entry
                break

        acl = {
            "role": role,
            "scope": {
                "type": target_type,
                "value": target_email,
            },
        }

        # If target_email doesn't have access or has a different role, update or add the ACL entry
        if existing_calendar_entry is None:
            print(f"\033[32mSharing {user_email}'s calendar with {target_email} as {role}\033[0m")
            service.acl().insert(calendarId=user_email, body=acl).execute()
        elif existing_calendar_entry["role"] != role:
            print(f"\033[33mUpdating {target_email}'s access to {user_email}'s calendar from {existing_calendar_entry['role']} to {role}\033[0m")
            rule_id = f"{target_type}:{target_email}"
            service.acl().update(calendarId=user_email, ruleId=rule_id, body=acl).execute()
        else:
            print(f"\033[33m{target_email} already has {role} access to {user_email}'s calendar\033[0m")

    except HttpError as error:
        print(f"\033[31mAn error occurred while sharing or updating the calendar: {error}\033[0m")



def audit_and_remove_unlisted_sharing(calendar_service, user_email, pre_set_rules):
    acl_list = calendar_service.acl().list(calendarId=user_email).execute()
    items = acl_list.get("items", [])
    for acl_entry in items:
        scope_type = acl_entry.get("scope", {}).get("type")
        if scope_type == "user" or scope_type == "group":
            sharing_email = acl_entry["scope"]["value"]
            role = acl_entry["role"]
            sharing_rule = (user_email, sharing_email, role)
            if sharing_rule not in pre_set_rules:
                # Add this condition to check if the user is not the primary owner
                if acl_entry["role"] != "owner" or sharing_email != user_email:
                    calendar_service.acl().delete(calendarId=user_email, ruleId=acl_entry["id"]).execute()
                    cprint(f"Removed {sharing_email} from {user_email} calendar", 'red')


def process_sharing_rules(credentials, user_email, rules_sheet_id, sheet_range, pre_set_rules):
    service = build("admin", "directory_v1", credentials=credentials)
    calendar_service = build("calendar", "v3", credentials=credentials)
    sheets_service = build("sheets", "v4", credentials=credentials)

    #show existing calendar permissions
    print_calendar_permissions(calendar_service, user_email)

    user_groups = get_user_groups(service, user_email)
    cprint(f"Found {len(user_groups)} group(s) for {user_email}", "blue")
    rules = get_rules(sheets_service, rules_sheet_id, sheet_range)
    cprint(f"Found {len(rules)} rule(s) in the Google Sheet", "blue")

    # Iterate through each group that the user is a part of
    for group in user_groups:
        # Iterate through each rule defined in the Google Sheet
        for rule in rules:
            # Check if the group email from the user's groups matches the User Group Email in the rule (rule[0])
            # and if the Managment Group Email (rule[1]) is not the same as the user's email
            if group["email"] == rule[0] and rule[1] != user_email:
                try:
                    # Share the user's calendar with the Managment Group Email (rule[1]) and grant the specified permission (rule[2])
                    share_calendar(calendar_service, user_email, rule[1], rule[2], target_type="group")
                    #print(f"\033[32mShared {user_email}'s calendar with {rule[1]} as {rule[2]}\033[0m")
                    # Add this sharing rule to the pre_set_rules set for later use in the audit_and_remove_unlisted_sharing function
                    pre_set_rules.add((user_email, rule[1], rule[2]))
                except HttpError as error:
                    print(f"\033[31mAn error occurred while sharing the calendar: {error}\033[0m")
    
    audit_and_remove_unlisted_sharing(calendar_service, user_email, pre_set_rules)
    print_calendar_permissions(calendar_service, user_email)  # Add this line

def print_calendar_permissions(service, user_email):
    try:
        acl_list = service.acl().list(calendarId=user_email).execute()
        items = acl_list.get("items", [])

        permissions = []
        for acl_entry in items:
            scope_type = acl_entry.get("scope", {}).get("type")
            if scope_type == "user" or scope_type == "group":
                email = acl_entry["scope"]["value"]
                role = acl_entry["role"]
                permissions.append((scope_type, email, role))

        headers = ["Type", "Email/Group", "Role"]
        print(f"\nCurrent permissions for {user_email}'s calendar:")
        print(tabulate(permissions, headers, tablefmt="grid"))

    except HttpError as error:
        print(f"\033[31mAn error occurred while retrieving calendar permissions: {error}\033[0m")



def main():
    cprint("Starting GWAC process", "cyan")

    # Read the config file
    config = configparser.ConfigParser()
    config.read("config.ini")
    gwac_config = config["GWAC"]

    parser = argparse.ArgumentParser(description="Google Workspace Automated Calendar Administration based on pre-set rules")
    parser.add_argument("--key-file", help="Path to the service account key file (in JSON format)", default=gwac_config.get("key_file"))
    parser.add_argument("--subject", help="Subject for the service account", default=gwac_config.get("subject"))
    parser.add_argument("--user-email", help="Email address of the user to manage", required=True)
    parser.add_argument("--rules-sheet-id", help="ID of the Google Sheet containing the pre-set rules", default=gwac_config.get("rules_sheet_id"))
    parser.add_argument("--sheet-range", help="Sheet range in the format 'SheetName!A1:C' that contains the pre-set rules", default=gwac_config.get("sheet_range"))

    args = parser.parse_args()

    credentials = get_credentials(args.key_file, args.subject)
    pre_set_rules = set()
    process_sharing_rules(credentials, args.user_email, args.rules_sheet_id, args.sheet_range, pre_set_rules)

    cprint("The Gwac is done! 🥑", "cyan")

if __name__ == "__main__":
    main()
