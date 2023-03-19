# GWACAMULI: (or GWAC) Google Workspace Automated Calendar Administration and Management Using Lists and Integration

GWACAMULI is a script designed to automate the management of Google Workspace calendars based on pre-set rules. It reads rules from a Google Sheet and shares calendars with specified groups or users, granting the appropriate permissions. The script also audits and removes any unlisted sharing permissions.

## Features

- Automatically share calendars based on rules from a Google Sheet
- Support for a config.ini file to manage settings easily
- Audit and remove unlisted sharing permissions
- Print current calendar permissions before and after processing the rules


## Prerequisites

1. You must have Python 3.6+ installed on your system.
- A Google Workspace account with admin privileges
- A Google Cloud Platform (GCP) project with the Calendar, Sheets, and Admin SDK APIs enabled
- A Google service account with domain-wide delegation
- A Google Sheet containing the calendar sharing rules


## Installation

1. Clone the repository or download the source code.
2. Install the required Python packages using the command:

```
    pip install -r requirements.txt
```
3. Duplicate the `config_example.ini` file and name it `config.ini`.
4. Open the `config.ini` file and update the fields with the appropriate values. (See Set up service account)

## Service Account for Dummies

The AI and I really struggled together with this part. We did our best to document our working steps (after about 15 wrong tries).

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Click on the hamburger menu (three horizontal lines) in the top left corner
4. Navigate to APIs & Services > Dashboard
5. Click on "+ ENABLE APIS AND SERVICES" at the top of the page
6. Search for the following APIs and enable them for your project:
   - Google Calendar API
   - Google Sheets API
   - Admin SDK API
7. Navigate to APIs & Services > Credentials
8. Click on "CREATE CREDENTIALS" at the top of the page and select "Service account"
9. Fill in the required details for your service account and click "CREATE"
10. Add the "Editor" role to your service account and click "CONTINUE"
11. Click "DONE" to finish creating the service account
12. Find the newly created service account in the list and click on the email address to view its details
13. Click on "ADD KEY" and select "JSON"
14. A JSON key file will be downloaded. Keep this file safe and secure, as it contains sensitive information

Now, you need to delegate domain-wide authority to your service account:

1. Log in to your Google Workspace admin account
2. Navigate to Security > API controls
3. Under "Domain-wide delegation", click on "MANAGE DOMAIN WIDE DELEGATION"
4. Click on "Add new" and fill in the following details:
   - Client ID: You can find this in the details of your service account on the Google Cloud Console
   - OAuth Scopes: `https://www.googleapis.com/auth/admin.directory.group.readonly, https://www.googleapis.com/auth/admin.directory.user.readonly, https://www.googleapis.com/auth/calendar, https://www.googleapis.com/auth/spreadsheets.readonly`
5. Click "Authorize" to finish setting up domain-wide delegation

Finally, update the `config.ini` file with the required information:

1. Duplicate the `config_example.ini` as `config.ini` in the same directory
2. Update the `key_file` field with the path to the JSON key file you downloaded earlier
3. Update the `subject` field with the email address of the admin account your service account is impersonating
4. Update the `rules_sheet_id` field with the ID of the Google Sheet containing the pre-set rules
5. Update the `sheet_range` field with the range in the format 'SheetName!A1:C' that contains the pre-set rules

Now you're ready to run the script!

## Rules Sheet Format

The rules sheet should contain three columns:

1. "User Group Email": The email address of the group the user is a part of.
2. "Management Group Email": The email address of the group or user the calendar will be shared with.
3. "Permission": The permission level assigned to the management group or user. Valid options include "writer", "reader", and "freeBusyReader". Using "owner" here will cause an error as you can not change the primary owner of a personal calendar.

Example:

User Group Email	Management Group Email	Permission
group1@example.com	managerGroup1@example.com	writer
group2@example.com	managerGroup2@example.com	reader
group3@example.com	managerGroup3@example.com	freeBusyReader
Make sure to update the sheet_range in the config.ini file to match the actual range of your rules sheet.

## Usage

Run the script:

    ```shell
    python gwac.py --user-email user@example.com
    ```

This script accepts the following optional arguments:

- --key-file: Path to the service account key file (in JSON format). Defaults to the value set in config.ini.
- --subject: Subject for the service account. Defaults to the value set in config.ini.
- --rules-sheet-id: ID of the Google Sheet containing the pre-set rules. Defaults to the value set in config.ini.
- --sheet-range: Sheet range in the format 'SheetName!A1:C' that contains the pre-set rules. Defaults to the value set in config.ini.  
- --dry-run: Allows you to see what changes the script would make without acutally applying them.

The script will share the user's calendar with specific management groups based on their group membership and remove any calendar sharing that is not on the pre-set rules list.

### Dry Run Mode

By including the `--dry-run` option when running the script, you can see the proposed changes without actually making any modifications to the calendar sharing settings. This mode is useful for testing the script and ensuring that your sharing rules are set up correctly before applying them to your calendars.

## Pre-set Rules Format

The pre-set rules should be stored in a Google Sheet with three columns:

1. User group email address.
2. Management group email address.
3. Permission level for the management group (e.g., "reader", "writer", "owner").

Example:


    user-group@example.com, management-group@example.com, reader


This rule indicates that if a user is part of `user-group@example.com`, their calendar should be shared with `management-group@example.com` with the "reader" permission level.

## Building the Script with ChatGPT-4

I developed this script using the help of ChatGPT-4, an advanced language model powered by OpenAI. The process of building the script was a collaboration between myself and the AI model, providing an interactive and efficient way to develop a complete solution.

### Struggles and Collaboration

I had attempted to write this script several times but faced challenges in tying together all the necessary components and learning various APIs. With the release of ChatGPT-4, I saw an opportunity to utilize the platform to collaboratively build the script, taking advantage of the AI's knowledge and ability to generate code.

### Interactive Development Process

The development process involved a series of prompts and responses between me and ChatGPT-4. I provided information about the desired functionality, and the AI generated code snippets and explanations to guide the development.

For example, I requested:

> "The command should have one input of user email address. The script should then query the google API to see what groups the user is a part of."

ChatGPT-4 provided relevant code snippets:

    ```python
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    ...
    def get_user_groups(user_email):
        ...
        results = service.groups().list(userKey=user_email).execute()
        groups = results.get("groups", [])
        return groups
    ```

As the development progressed, I provided additional requirements and clarified existing ones, such as:

> "What if I wanted to add a function that audits a user and removes any sharing that is not on the list?"

ChatGPT-4 adjusted the code accordingly, generating a complete script that met my needs.

### Creating the README

I also requested help in creating a README.md file for the script:

> "Write a README.md for this script"

ChatGPT-4 generated an initial version, which I reviewed and provided feedback on. The AI then incorporated my feedback and refined the README.md content.

The process of writing this README, including the section you are reading now, demonstrates how I worked together with ChatGPT-4 to create comprehensive documentation for the script.

### Conclusion

The collaboration with ChatGPT-4 enabled me to overcome previous struggles and build a complete script that achieves the desired functionality. This interactive development process showcases the potential of AI-assisted programming, providing an efficient way to learn, generate code, and create documentation.

