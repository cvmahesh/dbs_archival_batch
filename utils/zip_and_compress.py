import os
import zipfile
import shutil
import utils.file_utils 
# List of compressed file extensions
COMPRESSED_EXTENSIONS = {".zip", ".rar", ".7z", ".gz", ".bz2", ".xz"}

def is_compressed(file_name):
    _, ext = os.path.splitext(file_name)
    return ext.lower() in COMPRESSED_EXTENSIONS

 

def move_file_to_compressed_archive(source_file, dest_dir, archive_name="compressed_files"):
 
    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)
    
    # Full path for the archive in the destination directory
    archive_path = os.path.join(dest_dir, f"{archive_name}.zip")
    
    # Create or append to the ZIP file
    with zipfile.ZipFile(archive_path, 'a', compression=zipfile.ZIP_DEFLATED) as zipf:
        # Add the file to the archive with its base name
        zipf.write(source_file, os.path.basename(source_file))
        src_stat_zip = os.stat(source_file) 
        os.utime(archive_path, (src_stat_zip.st_atime, src_stat_zip.st_mtime))
        
    # Remove the original file after compression
    os.remove(source_file)
    
    print(f"Moved and compressed '{source_file}' into archive: {archive_path}")



def compress_with_best_compression(source_dir, dest_dir, archive_name="compressed_files"):
 
    # Ensure destination directory exists
    os.makedirs(dest_dir, exist_ok=True)
    
    # Full path for the archive in the destination directory
    archive_path = os.path.join(dest_dir, f"{archive_name}.zip")
    source_path = os.path.join(source_dir, f"{archive_name}")
    # Create the ZIP file with maximum compression
    with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Add file to the archive with a relative path
                arcname = os.path.relpath(file_path, start=source_dir)
                zipf.write(file_path, arcname)
                # Delete the original file after adding it to the archive
                os.remove(source_path)
    
    print(f"Compressed files with maximum compression: {archive_path}")


def zip_uncompressed_files(folder_path):
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

#move from archived dir to base directory 
def move_and_unzip_file(src_zip_path, dest_dir):
    # Ensure the destination directory exists
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Extract the filename from the source ZIP path
    zip_filename = os.path.basename(src_zip_path)
    
    # Create the full path to where the ZIP file will be moved
    dest_zip_path = os.path.join(dest_dir, zip_filename)

    try:
        # Move the ZIP file to the destination directory
        print(f"STEP 1")
        src_stat_zip = os.stat(src_zip_path) 
        print(f"STEP 2")
        shutil.move(src_zip_path, dest_zip_path)
        print(f"STEP 3")
        os.utime(dest_zip_path, (src_stat_zip.st_atime, src_stat_zip.st_mtime))
        print(f"ZIP file moved to: {dest_zip_path}")

        # Unzip the file in the destination directory
        with zipfile.ZipFile(dest_zip_path, 'r') as zip_ref:
            # Extract all the contents of the zip file into the destination directory
            zip_ref.extractall(dest_dir)
            print(f"ZIP file {zip_filename} unzipped successfully into: {dest_dir}")
        
        # Optionally remove the ZIP file after extracting (if you don't need it anymore)
        os.remove(dest_zip_path)
        #os.remove(src_zip_path)
        print(f"Removed the src_zip_path ZIP file: {src_zip_path}")
        print(f"Removed the dest_zip_path ZIP file: {dest_zip_path}")
        
    except Exception as e:
        print(f"Error: {e}")

# # Example usage
# folder_to_zip = "C:\\workspace\\testing\\delete\\folder1"  # Replace with the path to your folder
# zip_uncompressed_files(folder_to_zip)


 
# Example Usage
# source_file_path = "/path/to/source/file.txt"
# destination_directory = "/path/to/destination"
# move_file_to_compressed_archive(source_file_path, destination_directory, archive_name="compressed_archive")




