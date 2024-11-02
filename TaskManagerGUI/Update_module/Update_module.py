import os
import requests
import shutil
import zipfile
import sys
import subprocess

VERSION = "v2.0.0"

class Update_module:
    def __init__(self):
        super().__init__()
        self.repo_owner = 'NikolasPapaki'
        self.repo_name = 'TaskManagerGUI'
        self.download_dir = 'downloads'
        self.executable_name = "python main.py"
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
        headers = {"Authorization": f"token {self.github_token}"}
        os.makedirs(self.download_dir, exist_ok=True)
        zip_path = os.path.join(self.download_dir, 'latest_release.zip')

        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        return zip_path

    def extract_zip(self, zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.download_dir)

    def check_for_updates(self):
        latest_version, _ = self.get_latest_version()
        current_version_number = int(self.current_version[1:].replace(".", ""))
        latest_version_number = int(latest_version[1:].replace(".", ""))

        return latest_version_number > current_version_number, latest_version

    def update_application(self):
        latest_version, zipball_url = self.get_latest_version()
        zip_path = self.download_zipball(zipball_url)
        self.extract_zip(zip_path)
        print("Update complete. Restarting the application...")
        self.restart_application()

    def restart_application(self):
        python = sys.executable
        if os.name == 'nt':
            subprocess.Popen([python] + sys.argv, creationflags=subprocess.DETACHED_PROCESS)
        else:
            subprocess.Popen([python] + sys.argv)
        sys.exit(0)


