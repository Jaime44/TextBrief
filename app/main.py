import os
import sys
import traceback

from dotenv import load_dotenv


from tools.logger import AppLogger
from tools.gmail.gmail_client import GmailClient
from tools.gmail.gmail_authenticator import GmailAuthenticator


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

def main():
    logger = AppLogger("main.log")
    path_relative_env_from_app = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config", ".env")

    try:
        env_vars = load_environment_variables(path_relative_env_from_app)
        authenticator = GmailAuthenticator(
            credentials_path=env_vars["creds_path"],
            token_path=env_vars["token_path"],
        )
        authenticator.authenticate(env_vars["scopes"])
        gmail_service = authenticator.get_service()
        gmail_client = GmailClient(gmail_service)
        profile = gmail_client.get_profile()
        profile = gmail_client.get_profile()
        profile = gmail_client.get_profile()
        logger.debug(f'------------------------------------------------------>> Profile: {profile}')

    except Exception as e:
        print(f"Application failed: {e}")
        _,_, exec_tb = sys.exc_info()
        line_number = exec_tb.tb_lineno if exec_tb else 'unknown'
        function_name = exec_tb.tb_frame.f_code.co_name if exec_tb else 'unknown'
        error_message = f"Application failed: '{function_name}' at line {line_number}: {e}"
        logger.error(error_message)

def clear_files_in_directory(directory: str="/home/jmorenos/workarea/githubRepo/smart-newsletters/logs/") -> None:
    """
    Clear the contents of all files in the given directory.
    
    Args:
        directory (str): Path to the target directory.
    
    Raises:
        FileNotFoundError: If the directory does not exist.
        Exception: If any command fails.
    """
    import subprocess
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    # Use shell command 'truncate' safely on each file
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            try:
                subprocess.run(["truncate", "-s", "0", file_path], check=True)
                # print(f"Cleared: {file_path}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to clear {file_path}: {e}")


if __name__ == "__main__":
    clear_files_in_directory()
    main()