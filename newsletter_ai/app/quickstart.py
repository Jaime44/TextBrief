import os.path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from newsletter_ai.tools.logger import AppLogger




# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def __show_users_labels_mailbox(service, user_id="me"):
  """Get a list of labels in the user's mailbox.
  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
  Returns:
    List of Labels found in the user's mailbox.
  """
  try:
    results = service.users().labels().list(userId=user_id).execute()
    labels = results.get("labels", [])
    if not labels:
      print("No labels found.")
      return
    print("Labels:")
    for label in labels:
      print(f"\tLabel id: {label['id']}, Label name: {label['name']}")
  except HttpError as error:
    print(f"An error occurred: {error}")
    return None

def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  creds_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS_DESKTOP_APP"] = "/home/jmorenos/workarea/githubRepo/smart-newsletters/secrets/deskapp_client_secret_credentials.json"
  token_path = os.environ["GOOGLE_APPLICATION_TOKENS_DESKTOP_APP"] = "/home/jmorenos/workarea/githubRepo/smart-newsletters/secrets/token.json"

  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(token_path):
    print("Loading credentials from token.json")
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    print("Refreshing or obtaining new credentials")
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          creds_path, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token_path, "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    __show_users_labels_mailbox(service)
  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()