# GWACAMULI: (or GWAC) Google Workspace Automated Calendar Administration and Management Using Lists and Integration

GWACAMULI is a script designed to automate the management of Google Workspace users' calendar sharing based on pre-set rules stored in a Google Sheet. It shares the user's calendar with specific management groups according to their group membership and removes any calendar sharing that is not included in the pre-set rules list.

## Prerequisites

1. You must have Python 3.6+ installed on your system.
2. You need to have the `google-auth`, `google-auth-httplib2`, and `google-api-python-client` Python packages installed. You can install them using the following command:

    ```
    pip install google-auth google-auth-httplib2 google-api-python-client
    ```

3. Enable the [Google Sheets API](https://developers.google.com/sheets/api/quickstart/python), [Google Calendar API](https://developers.google.com/calendar/quickstart/python), and [Admin SDK API](https://developers.google.com/admin-sdk/directory/v1/guides/prerequisites) for your Google Cloud project. Obtain service account JSON key files for each API and grant the necessary permissions:

   - Google Sheets API: Read access to the Google Sheet containing the rules.
   - Google Calendar API: Manage calendar sharing.
   - Admin SDK API: Read access to the user's group membership.

4. Replace the placeholder values in the script with the appropriate values, such as the path to the API credentials files, the Google Sheet ID, and the range containing the rules.

## Usage

1. Update the `user_email` variable in the script with the email address of the user whose calendar you want to manage:

    ```python
    if __name__ == "__main__":
        user_email = "user@example.com"
        main(user_email)
    ```

2. Run the script:

    ```
    python gwac.py
    ```

The script will share the user's calendar with specific management groups based on their group membership and remove any calendar sharing that is not on the pre-set rules list.

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

