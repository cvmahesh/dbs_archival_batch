import os
import shutil
import zipfile
from datetime import datetime, timedelta
import pymysql
import logging
import yaml

# Program will create archival based on the run date in the backup directory 
# Program deletes the files that are older than configured days. 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Load configuration from YAML file
def load_config(config_file='file_config.yaml'):
    # Get the path to the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #print(f"Script Dir: {script_dir}")

    # Get the path to the config file one level up
    config_path = os.path.join(script_dir, '', config_file)
    print(f"Script Dir: {script_dir} \t config_path : {config_path} ")
    
    # Ensure the config file is accessible
    if not os.path.exists(config_path):
        logging.error(f"Config file not found at {config_path}")
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    # Load the YAML config file
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        print(f"config : {config}")
    return config

# Load the configuration details
config = load_config()

# MariaDB connection details from YAML config
DB_HOST = config['mariadb']['host']
DB_USER = config['mariadb']['user']
DB_PASSWORD = config['mariadb']['password']
DB_NAME = config['mariadb']['database']
PORT = config['mariadb']['port']

# Source and Destination directories from YAML config
SOURCE_BASE_DIR = config['source_base_dir']
DEST_BASE_DIR = config['dest_base_dir']

# Directories to ignore from YAML config
IGNORE_DIRS = config['ignore_dirs']

# SQL query for archival config from YAML
ARCHIVAL_CONFIG_QUERY = config['archival_config_query']

# Function to get directories to archive from the archival_config table
def get_archival_config():
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=PORT 
    )
    print(f"connection  : {connection}   ")
    directories_to_archive = []

    try:
        with connection.cursor() as cursor:
            cursor.execute(ARCHIVAL_CONFIG_QUERY)
            result = cursor.fetchall()
            for row in result:
                dir_name, archival_period = row
                directories_to_archive.append((dir_name, archival_period))
        print(f"directories_to_archive  : {directories_to_archive} \t config_path : {dir_name} ")
    except Exception as e:
        logging.error(f"Error fetching archival config: {e}")
    finally:
        connection.close()

    return directories_to_archive

# Function to archive a directory
def archive_directory(source_dir, dest_dir):
    # Check if directory exists
    if not os.path.exists(source_dir):
        logging.warning(f"Source directory {source_dir} does not exist.")
        return
    
    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Create a zip file to archive the directory
    archive_name = os.path.join(dest_dir, f"{os.path.basename(source_dir)}_{datetime.now().strftime('%Y%m%d')}.zip")
    
    logging.info(f"Creating archive for {source_dir} at {archive_name}")

    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as archive:
        for foldername, subfolders, filenames in os.walk(source_dir):
            # Skip ignored directories
            if any(foldername.startswith(ignored_dir) for ignored_dir in IGNORE_DIRS):
                continue
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, source_dir)  # To store directory structure
                archive.write(file_path, arcname)
    
    logging.info(f"Archive created: {archive_name}")

# Function to check if a directory should be archived based on archival period
def should_archive(dir_name, archival_period):
    # Example: If archival_period is a number of days (e.g., 30), check if the directory should be archived
    # This can be customized based on your business logic (e.g., last modified date check).
    print(f"dir_name : {dir_name} \t archival_period : {archival_period} ")
    current_date = datetime.now()
    # Assuming archival_period is a number of days
    threshold_date = current_date - timedelta(days=archival_period)

    # Check the last modified date of the directory
    dir_last_modified = datetime.fromtimestamp(os.path.getmtime(dir_name))
    return dir_last_modified < threshold_date

# Function to delete directories older than the configured archival period
def delete_old_folders(dir_name, archival_period):
    # Check if the directory exists
    if not os.path.exists(dir_name):
        logging.warning(f"Directory {dir_name} does not exist.")
        return
    
    # Calculate the threshold date for deletion
    current_date = datetime.now()
    threshold_date = current_date - timedelta(days=archival_period)

    # Check the last modified date of the directory
    dir_last_modified = datetime.fromtimestamp(os.path.getmtime(dir_name))

    if dir_last_modified < threshold_date:
        try:
            # Remove the directory and its contents
            shutil.rmtree(dir_name)
            logging.info(f"Deleted old directory: {dir_name}")
        except Exception as e:
            logging.error(f"Error deleting directory {dir_name}: {e}")

# Main function to perform the archival process
def perform_archival():
    # Fetch the configuration for directories and archival periods
    directories_to_archive = get_archival_config()
    
    # Get the current date for creating the destination directory
    current_date_str = datetime.now().strftime('%Y%m%d')

    
    print(f"\n\ndirectories_to_archive: {directories_to_archive}, current_date_str: {current_date_str}")

    for dir_name, archival_period in directories_to_archive:
        # Construct the source and destination paths
        source_dir = os.path.join(SOURCE_BASE_DIR, dir_name)
        dest_dir = os.path.join(DEST_BASE_DIR, current_date_str, dir_name)

        # Check if the directory should be archived
        if should_archive(source_dir, archival_period):
            # Archive the directory
            archive_directory(source_dir, dest_dir)
        else:
            logging.info(f"Skipping {source_dir}, not yet time for archival.")
        
        # After archiving, delete directories older than the archival period
        delete_old_folders(source_dir, archival_period)

if __name__ == "__main__":
    perform_archival()
