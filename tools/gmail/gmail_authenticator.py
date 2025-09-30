import os
import sys
import traceback

from typing import List
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import Resource, build
from google_auth_oauthlib.flow import InstalledAppFlow


from tools.logger import AppLogger


class AuthenticationError(Exception):
    pass

class GmailAuthenticator:
    """
    Handles Gmail API authentication separately.
    Supports token storage, refresh, and OAuth2 flow.
    """

    def __init__(self, credentials_path: str, token_path: str):
        """
        Initialize GmailAuthenticator.

        Args:
            credentials_path (str): Path to client secrets JSON file.
            token_path (str): Path to store the OAuth token JSON.
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.logger = AppLogger("gmail_authenticator.log")
        self.creds = None

    def authenticate(self, scopes: List[str]) -> Credentials:
        """
        Authenticate the user and return valid credentials.

        Args:
            scopes (List[str]): List of OAuth scopes required for the API.

        Returns:
            Credentials: Authorized Google API credentials.

        Raises:
            AuthenticationError: If authentication fails for any reason.
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

    def get_service(self, api_name: str = "gmail", api_version: str = "v1") -> Resource:
            """
            Returns an authorized Gmail API service object.

            Args:
                api_name (str): Name of the Google API. Default is 'gmail'.
                api_version (str): Version of the API. Default is 'v1'.

            Returns:
                Resource: Authorized Google API service object.

            Raises:
                AuthenticationError: If credentials are invalid or missing.
            """
            if not self.creds:
                raise AuthenticationError("No valid credentials found. Call 'authenticate' first.")
            try:
                service = build(api_name, api_version, credentials=self.creds)
                self.logger.info(f"Gmail service created for {api_name} {api_version}")
                return service
            except Exception as e:
                _, _, exec_tb = sys.exc_info()
                line_number = exec_tb.tb_lineno if exec_tb else "unknown"
                function_name = exec_tb.tb_frame.f_code.co_name if exec_tb else "unknown"

                self.logger.error(
                    f"Failed to create service in function '{function_name}' at line {line_number}: {e}"
                )
                raise AuthenticationError("Failed to create Gmail service") from e