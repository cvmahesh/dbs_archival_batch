import os
import yaml
from datetime import datetime, timedelta

# Load the configuration from YAML
def load_config( ):
    # with open(config_file, 'r') as file:
    #     config = yaml.safe_load(file)
    # return config

    with open('file_config.yaml', 'r') as file:
        return yaml.safe_load(file)
    
# Ensure base folder exists
def ensure_base_folder(base_path):
    if not os.path.exists(base_path):
        os.makedirs(base_path)

# Get the current list of folders
def get_current_folders(base_path):
    return sorted([f for f in os.listdir(base_path) if f.startswith("Day")], key=lambda x: int(x[3:]))

# Create a new folder
def create_new_folder(base_path, folder_name):
    folder_path = os.path.join(base_path, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# Delete the oldest folder
def delete_oldest_folder(base_path, folders):
    oldest_folder = folders[0]
    folder_path = os.path.join(base_path, oldest_folder)
    if os.path.exists(folder_path):
        os.rmdir(folder_path)
        print(f"Deleted folder: {oldest_folder}")

 
def delete_file(file_path):
    
    try:
        # Check if the file exists
        if os.path.exists(file_path):
            # Delete the file
            os.remove(file_path)
            print(f"File deleted successfully: {file_path}")
            return True
        else:
            print(f"File does not exist: {file_path}")
            return False
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")
        return False

 

def delete_old_folders_days(base_path, days_threshold):
 
    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=days_threshold)

    try:
        # Iterate through items in the base path
        for folder_name in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder_name)

            # Check if it's a directory and the name is in yyyymmdd format
            if os.path.isdir(folder_path) and len(folder_name) == 8 and folder_name.isdigit():
                try:
                    # Convert folder name to a date object
                    folder_date = datetime.strptime(folder_name, '%Y%m%d')

                    # Check if the folder date is older than the cutoff date
                    if folder_date < cutoff_date:
                        # Delete the folder
                        print(f"Deleting folder: {folder_path}")
                        os.rmdir(folder_path)  # Use os.rmdir for empty directories
                except ValueError:
                    print(f"Skipping folder with invalid date format: {folder_name}")
    except Exception as e:
        print(f"Error processing folders: {e}")

# Rename folders sequentially
def rename_folders(base_path, folders):
    for index, folder in enumerate(folders):
        old_path = os.path.join(base_path, folder)
        new_name = f"Day{index + 1}"
        new_path = os.path.join(base_path, new_name)
        if old_path != new_path:
            os.rename(old_path, new_path)
            print(f"Renamed {folder} to {new_name}")

# Main logic for rolling folder management
def manage_folders(config):
   
    max_days = config["max_days"]
    base_path = config["base_path"]

    # Ensure the base folder exists
    ensure_base_folder(base_path)

    # Get the current list of folders
    folders = get_current_folders(base_path)

    # Delete the oldest folder if limit exceeded
    if len(folders) >= max_days:
        delete_oldest_folder(base_path, folders)
        folders = folders[1:]  # Remove the oldest folder from the list

    # Rename folders to maintain sequential order
    rename_folders(base_path, folders)

    # Create the next folder
    new_folder_name = f"Day{len(folders) + 1}"
    create_new_folder(base_path, new_folder_name)
    print(f"Created folder: {new_folder_name}")

# Run the script
if __name__ == "__main__":
     # Load config
    config = load_config()
    manage_folders(config)
