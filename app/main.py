import os
import sys

from typing import Dict, Any
from dotenv import load_dotenv


from tools.logger import AppLogger
from tools.gmail.gmail_client import GmailClient
from tools.gmail.gmail_authenticator import GmailAuthenticator
from tools import utils as Utils


def load_environment_variables(env_path: str = ".env") -> dict:
    """
    Load and prepare environment variables from a .env file.

    :param env_path: Path to the .env file
    :return: Dictionary containing the key environment variables
    :raises FileNotFoundError: if the .env file does not exist
    :raises KeyError: if required environment variables are missing
    """
    # Load .env file
    if not os.path.exists(env_path):
        raise FileNotFoundError(f".env file not found at path: {env_path}")
    load_dotenv(dotenv_path=env_path)
    # Retrieve required variables
    try:
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_DESKTOP_APP")
        token_path = os.getenv("GOOGLE_APPLICATION_TOKENS_DESKTOP_APP")
        # If modifying these scopes, delete the file token.json.
        scopes = os.getenv("GOOGLE_SCOPES")
        if not creds_path or not token_path or not scopes:
            raise KeyError("One or more required environment variables are missing")
        return {
            "creds_path": str(creds_path),
            "token_path": str(token_path),
            "scopes": [scope.strip() for scope in scopes.split(",")]
        }
    except KeyError as e:
        raise KeyError(f"Error loading environment variables: {e}")

# def main():
#     logger = AppLogger("main.log")
#     path_relative_env_from_app = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config", ".env")

#     try:
#         env_vars = load_environment_variables(path_relative_env_from_app)
#         authenticator = GmailAuthenticator(
#             credentials_path=env_vars["creds_path"],
#             token_path=env_vars["token_path"],
#         )
#         authenticator.authenticate(env_vars["scopes"])
#         gmail_service = authenticator.get_service()
#         gmail_client = GmailClient(gmail_service)
#         profile = gmail_client.get_profile()
#         profile = gmail_client.get_profile()
#         profile = gmail_client.get_profile()
#         logger.debug(f'------------------------------------------------------>> Profile: {profile}')

#     except Exception as e:
#         print(f"Application failed: {e}")
#         _,_, exec_tb = sys.exc_info()
#         line_number = exec_tb.tb_lineno if exec_tb else 'unknown'
#         function_name = exec_tb.tb_frame.f_code.co_name if exec_tb else 'unknown'
#         error_message = f"Application failed: '{function_name}' at line {line_number}: {e}"
#         logger.error(error_message)


def run_user_session(user_email: str, env_vars: Dict[str, Any], logger: AppLogger) -> None:
    """
    Authenticate a user, create Gmail service and run Gmail API operations.

    Args:
        user_email (str): Gmail address of the user.
        env_vars (dict): Environment variables including credentials paths and scopes.
        logger (AppLogger): Logger instance for recording operations.
    """
    try:
        authenticator = GmailAuthenticator(credentials_path=env_vars["creds_path"])

        # Token path per user
        token_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tokens")
        os.makedirs(token_dir, exist_ok=True)
        user_token_path = os.path.join(token_dir, f"{user_email.replace('@','_at_')}.json")

        # Authenticate user
        creds = authenticator.authenticate_user(
            user_email=user_email,
            scopes=env_vars["scopes"],
            token_storage_path=user_token_path
        )

        # Create Gmail service and client
        gmail_service = authenticator.get_service_for_user(creds)
        gmail_client = GmailClient(gmail_service)

        # Example operation: get profile
        profile = gmail_client.get_profile()
        logger.info(f"User {user_email} profile: {profile}")

    except Exception as e:
        _, _, exec_tb = sys.exc_info()
        line_number = exec_tb.tb_lineno if exec_tb else "unknown"
        function_name = exec_tb.tb_frame.f_code.co_name if exec_tb else "unknown"
        error_message = f"User session failed for '{user_email}' in '{function_name}' at line {line_number}: {e}"
        logger.error(error_message)
        print(error_message)


def main():
    """
    Main entry point: setup logger, load environment, prompt user and run session.
    """
    logger = AppLogger("main.log")
    path_relative_env_from_app = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../config",
        ".env"
    )

    try:
        env_vars = load_environment_variables(path_relative_env_from_app)

        # Prompt user for email
        user_email = input("Enter your Gmail address: ").strip()
        if not user_email:
            raise ValueError("A valid Gmail address is required")

        # Run user session (auth + Gmail operations)
        run_user_session(user_email, env_vars, logger)

    except Exception as e:
        _, _, exec_tb = sys.exc_info()
        line_number = exec_tb.tb_lineno if exec_tb else "unknown"
        function_name = exec_tb.tb_frame.f_code.co_name if exec_tb else "unknown"
        error_message = f"Application failed in '{function_name}' at line {line_number}: {e}"
        logger.error(error_message)
        print(error_message)

if __name__ == "__main__":
    Utils.clear_files_in_directory()
    main()
