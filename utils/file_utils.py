import os
# import yaml
from datetime import datetime, timedelta
import shutil
import logging
import batch_logger.archival_logger


# batch_logger.archival_logger.setup_logging() 
# logger = batch_logger.archival_logger.getLogger(__name__)
# logger.info(f"Logging set....")

logger = logging.getLogger(__name__)
logger.info(f"Logging set....")

def find_all_subdirectories(base_folder):
    subdirectories = []
    for root, dirs, files in os.walk(base_folder):
        for directory in dirs:
            # Get the full path
            full_path = os.path.join(root, directory)
            # Calculate the relative path
            relative_path = os.path.relpath(full_path, base_folder)
            subdirectories.append(relative_path)
    return subdirectories


def get_last_n_days(n_days):
    """
    Generate the last n days in 'yyyymmdd' format.
    """
    today = datetime.today()
    last_n_days = []
    for i in range(n_days):
        day = today - timedelta(days=i)
        last_n_days.append(day.strftime('%Y%m%d'))
    return last_n_days


def clean_directory(dest_base_dir, last_15_days):
    """
    Delete all directories and files in dest_base_dir apart from the ones in last_15_days.
    """

    logger.info(f"...dest_base_dir: "+dest_base_dir)
    # List all files and directories in dest_base_dir
    for item in os.listdir(dest_base_dir):
        item_path = os.path.join(dest_base_dir, item)
        
        # Check if the item is a directory
        if os.path.isdir(item_path):
            # If the directory name is not in last_15_days, delete it
            if item not in last_15_days:
                logger.info(f"Deleting directory: {item_path}")
                shutil.rmtree(item_path)  # Delete the directory and its contents
            else:
                logger.info(f"Keeping directory: {item_path}")
        
        # Check if the item is a file
        elif os.path.isfile(item_path):
            # If the file name (without extension) is not in last_15_days, delete it
            if item.split('.')[0] not in last_15_days:
                logger.info(f"Deleting file: {item_path}")
                os.remove(item_path)  # Delete the file
            else:
                logger.info(f"Keeping file: {item_path}")


 
# Run the script
if __name__ == "__main__":
    print("Hi")


    logger.info("Start...:")
    base_folder = "C:\\workspace\\testing\\TARGET_DIR"
    subdirs = find_all_subdirectories(base_folder)
    logger.info("Subdirectories:")
    for subdir in subdirs:
        logger.info(subdir)


    # Example usage
    dest_base_dir = r"C:\\workspace\\testing\\RollingFolders"  # Change this to your directory path
    last_15_days = get_last_n_days(15)
    logger.info(f"last_15_days:{last_15_days}")
    # Clean the directory by deleting files and directories that aren't in the last 15 days
    clean_directory(dest_base_dir, last_15_days)