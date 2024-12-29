import os
import zipfile
import utils.file_utils 
# List of compressed file extensions
COMPRESSED_EXTENSIONS = {".zip", ".rar", ".7z", ".gz", ".bz2", ".xz"}

def is_compressed(file_name):
    """
    Checks if a file is already compressed based on its extension.

    :param file_name: Name of the file to check.
    :return: True if the file is compressed, False otherwise.
    """
    _, ext = os.path.splitext(file_name)
    return ext.lower() in COMPRESSED_EXTENSIONS

def zip_uncompressed_files(folder_path):
    
    """
    Zips only the uncompressed files in a folder into individual zip files.

    :param folder_path: Path to the folder containing files to zip.
    """
    print(f"Zipping files at the destination :: '{folder_path}'  ")
    if not os.path.isdir(folder_path):
        print(f"The specified path '{folder_path}' is not a valid directory.")
        return

    files = os.listdir(folder_path)

    for file in files:
        file_path = os.path.join(folder_path, file)

        # Skip directories and compressed files
        if os.path.isfile(file_path) and not is_compressed(file):
            zip_name = f"{file}.zip"
            zip_path = os.path.join(folder_path, zip_name)

            # Use maximum compression
            # with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            #     zipf.write(file_path, arcname=file)
            
            # Create a ZIP file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.write(file_path)
                #print("File added to archive.")
            utils.file_utils.delete_file(file_path)
            print(f"Zipped '{file}' into '{zip_name}' with best compression")
        elif is_compressed(file):
            print(f"Skipped '{file}' (already compressed)")

# Example usage
folder_to_zip = "C:\\workspace\\testing\\delete\\folder1"  # Replace with the path to your folder
zip_uncompressed_files(folder_to_zip)
