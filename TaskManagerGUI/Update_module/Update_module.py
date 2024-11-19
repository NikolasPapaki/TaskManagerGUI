import os
import shutil
import zipfile
import sys
import subprocess
import certifi

# Use the bundled certifi file if running as an executable
if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
    certifi_path = os.path.join(sys._MEIPASS, 'certifi', 'cacert.pem')
else:  # Fallback for normal Python execution
    certifi_path = certifi.where()

# Set the path for requests
import requests
requests.utils.DEFAULT_CA_BUNDLE_PATH = certifi_path

# EXECUTABLE_NAME = "python main.py"
EXECUTABLE_NAME = "TaskManager.exe"
VERSION = "v4.0.0"

def restart_application_executable():
    """
    Restarts the current PyInstaller-built executable.
    """
    try:
        executable_path = sys.executable  # Path to the current executable
        if os.name == 'nt':
            # Windows-specific: detach the process
            subprocess.Popen([executable_path], creationflags=subprocess.DETACHED_PROCESS)
        else:
            # Unix-based systems
            subprocess.Popen([executable_path])
    except Exception as e:
        print(f"Error while restarting the application: {e}")
    finally:
        # Exit the current instance
        sys.exit(0)

class Update_module:
    def __init__(self):
        super().__init__()
        self.repo_owner = 'NikolasPapaki'
        self.repo_name = 'TaskManagerGUI_app'
        self.download_dir = 'downloads'
        self.executable_name = EXECUTABLE_NAME
        self.current_version = VERSION
        self.latest_release_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest'

    def get_latest_version(self):
        response = requests.get(self.latest_release_url)
        response.raise_for_status()
        latest_release = response.json()

        if 'zipball_url' not in latest_release:
            raise ValueError("No zipball_url found in the latest release.")

        return latest_release["tag_name"], latest_release["zipball_url"]

    def download_zipball(self, url):
        os.makedirs(self.download_dir, exist_ok=True)
        zip_path = os.path.join(self.download_dir, 'latest_release.zip')

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        return zip_path

    def extract_zip(self, zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.download_dir)

            # Check if TaskManager.exe is in the extracted files and move it
            extracted_files = zip_ref.namelist()  # Get a list of extracted files
            for file in extracted_files:
                if self.executable_name in file:
                    # Move TaskManager.exe to the current working directory
                    shutil.move(os.path.join(self.download_dir, file), os.path.join(os.getcwd(), self.executable_name))

        # Delete the zip file after extraction
        os.remove(zip_path)

    def check_for_updates(self):
        latest_version, _ = self.get_latest_version()
        current_version_number = int(self.current_version[1:].replace(".", ""))
        latest_version_number = int(latest_version[1:].replace(".", ""))

        return latest_version_number > current_version_number, latest_version

    def update_application(self):
        latest_version, zipball_url = self.get_latest_version()
        zip_path = self.download_zipball(zipball_url)
        self.extract_zip(zip_path)
        self.restart_application()

    def restart_application(self):
        restart_application(self.executable_name)
