from datetime import datetime
import os

# Method to get folder name based on system date
def get_folder_name_from_system_date():
    current_date = datetime.now()
    folder_name = current_date.strftime('%Y%m%d')
    return folder_name

# Method to get folder name based on argument date
def get_folder_name_from_argument_date(date_string):
    """
    Convert the input date string in 'YYYY-MM-DD' format to 'yyyymmdd'.

    Args:
        date_string (str): The input date in 'YYYY-MM-DD' format.

    Returns:
        str: The folder name in 'yyyymmdd' format.
    """
    try:
        input_date = datetime.strptime(date_string, '%Y-%m-%d')
        folder_name = input_date.strftime('%Y%m%d')
        return folder_name
    except ValueError as e:
        print(f"Error: Invalid date format. Use 'YYYY-MM-DD'. {e}")
        return None




# Method to get the path separator based on the operating system
def get_path_separator():
    """
    Returns the path separator for the current operating system.

    Returns:
        str: The path separator (e.g., '/' for Unix-like systems, '\\' for Windows).
    """
    return os.path.sep



# Example Usage
if __name__ == "__main__":
    # Get folder name based on system date
    print("Folder name from system date:", get_folder_name_from_system_date())

    # Get folder name based on argument date
    sample_date = "2023-12-28"
    print("Folder name from argument date:", get_folder_name_from_argument_date(sample_date))

    # Invalid date example
    invalid_date = "28-12-2023"
    print("Invalid date example:", get_folder_name_from_argument_date(invalid_date))


    path_separator = get_path_separator()
    print(f"Path separator for the current OS: '{path_separator}'")