import os
import sys
import traceback

from typing import Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


from tools.logger import AppLogger


class AuthenticationError(Exception):
    pass

class GmailAuthenticator:
    """
    Handles Gmail API authentication separately.
    Supports token storage, refresh, and OAuth2 flow.
    """

    def __init__(self, credentials_path: str, token_path: str, logger: Optional[AppLogger] = None):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.logger = logger or AppLogger("gmail_authenticator.log")
        self.creds = None

    def authenticate(self, scopes: list[str]):
        """
        Authenticate and return valid credentials.
        """
        try:
            if os.path.exists(self.token_path):
                self.creds = Credentials.from_authorized_user_file(self.token_path, scopes)
                self.logger.info("Loaded existing token")
            # If there are no valid credentials, go through OAuth flow
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                    self.logger.info("Token refreshed")
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, scopes)
                    self.creds = flow.run_local_server(port=0)
                    self.logger.info("New token obtained via OAuth flow")
                # Save the credentials for next time
                with open(self.token_path, 'w') as token_file:
                    token_file.write(self.creds.to_json())
        except Exception as e:
            _,_, exec_tb = sys.exc_info()
            line_number = exec_tb.tb_lineno if exec_tb else 'unknown'
            function_name = exec_tb.tb_frame.f_code.co_name if exec_tb else 'unknown'
            # Log full traceback + function name
            self.logger.error(
                f"Authentication failed in function '{function_name}' at line {line_number}: {e}"
            )
            raise AuthenticationError("Gmail authentication failed") from e

        return self.creds
