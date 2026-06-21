import os
import urllib.request
from urllib.error import URLError, HTTPError

def download_file(url: str, destination_path: str) -> bool:
    """
    Downloads a file from a URL and saves it to the specified destination path.
    Automatically creates missing destination directories.
    """
    try:
        # 1. Get the absolute path and extract the target directory
        abs_destination = os.path.abspath(destination_path)
        destination_dir = os.path.dirname(abs_destination)

        # 2. Ensure target directory exists
        if destination_dir and not os.path.exists(destination_dir):
            print(f"Creating directory: {destination_dir}")
            os.makedirs(destination_dir, exist_ok=True)

        print(f"Downloading: {url}")
        print(f"Saving to:   {abs_destination}")

        # 3. Stream the file down to the machine
        # urllib.request.urlretrieve is efficient and clean for direct file saves
        urllib.request.urlretrieve(url, abs_destination)
        
        print("Download completed successfully!")
        return True

    except (URLError, HTTPError) as e:
        print(f"Network error during download: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
