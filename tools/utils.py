import os


def clear_files_in_directory() -> None:
    """
    Clear the contents of all files in the 'logs' directory relative
    to the directory from which the script is executed.

    Raises:
        FileNotFoundError: If the logs directory does not exist.
        Exception: If any command fails.
    """
    import subprocess
    # Construir la ruta absoluta del subdirectorio 'logs'
    current_dir = os.getcwd()  # directorio desde donde se ejecuta el script
    directory = os.path.join(current_dir, "logs")

    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Logs directory does not exist: {directory}")

    # Vaciar cada archivo usando 'truncate' de manera segura
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            try:
                subprocess.run(["truncate", "-s", "0", file_path], check=True)
                # print(f"Cleared: {file_path}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to clear {file_path}: {e}")
