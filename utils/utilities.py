from datetime import datetime
import os

# Method to get folder name based on system date
def get_folder_name_from_system_date():
    current_date = datetime.now()
    folder_name = current_date.strftime('%Y%m%d')
    return folder_name

# Method to get folder name based on argument date
def get_folder_name_from_argument_date(date_string):

    try:
        input_date = datetime.strptime(date_string, '%Y-%m-%d')
        folder_name = input_date.strftime('%Y%m%d')
        return folder_name
    except ValueError as e:
        print(f"Error: Invalid date format. Use 'YYYY-MM-DD'. {e}")
        return None




# Method to get the path separator based on the operating system
def get_path_separator():
 
    return os.path.sep



# Example Usage
if __name__ == "__main__":
    # Get folder name based on system date
    print("Folder name from system date:", get_folder_name_from_system_date())

    # Get folder name based on argument date
    sample_date = "2024-12-28"
    print("Folder name from argument date:", get_folder_name_from_argument_date(sample_date))

    # Invalid date example
    invalid_date = "28-12-2024"
    print("Invalid date example:", get_folder_name_from_argument_date(invalid_date))


    path_separator = get_path_separator()
    print(f"Path separator for the current OS: '{path_separator}'")


    import uuid

    # Create a UUID using SHA-1 hashing
    namespace = uuid.NAMESPACE_DNS
    name = "example.com"
    name_based_uuid_sha1 = uuid.uuid5(namespace, name)

    print(f"Name-based UUID (SHA-1): {name_based_uuid_sha1}")


 

    # Generate a random UUID
    random_uuid = uuid.uuid4()

    print(f"Random UUID: {random_uuid}")
