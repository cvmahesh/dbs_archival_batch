import os
import shutil
import time
import yaml
from datetime import datetime, timedelta
import mysql.connector
import logging
import logging.config
import yaml
import sys
from datetime import date
import argparse
from mysql.connector import Error
# import MySQLdb
import mod_mariadb 
import utils.zip_and_compress
import utils.file_utils
import utils.utilities
import uuid


# Load YAML configuration file
def load_config():
    with open('file_config.yaml', 'r') as file:
        return yaml.safe_load(file)

# Logging configuration from YAML
def setup_logging():
    try:
        log_config = yaml.safe_load('logging_config.YAML')        
        logging.config.dictConfig(log_config)
        logger = logging.getLogger(__name__)
    except ValueError as e:
        print(f"Failed to configure logging: {e}")

# Function to move files based on age
def move_files(random_uuid, config, src_folder, dest_folder, age_days, connection):
    current_time = time.time()
    
    src_folder = config['source_base_dir'] + src_folder 
    dest_base_dir= config['dest_base_dir']
    dest_new_dir = utils.utilities.get_folder_name_from_system_date() +utils.utilities.get_path_separator()+dest_folder
    dest_folder = dest_base_dir + dest_new_dir
    #config['dest_base_dir'] + utils.utilities.get_folder_name_from_system_date() +utils.utilities.get_path_separator()+dest_folder

    #Create destination folder if not exit
    
    utils.file_utils.create_new_folder( dest_base_dir ,dest_new_dir)

    print(f"Move from {src_folder} to {dest_folder}")
    
    # cursor = connection.cursor()



    # Iterate through files in the source folder
    for filename in os.listdir(src_folder):
        file_path = os.path.join(src_folder, filename)
        
        # Skip if it's not a file
        if not os.path.isfile(file_path):
            continue
        
        # Get the file's last modified time
        file_mod_time = os.path.getmtime(file_path)
        file_age_days = (current_time - file_mod_time) / (60 * 60 * 24)
        
        # If the file is older than the threshold, move it
        if file_age_days >= age_days:
            dest_path = os.path.join(dest_folder, filename)
            try:
                print(f"Moving file from {file_path} to {dest_path}  " )
                #shutil.move(file_path, dest_path)
                utils.zip_and_compress.move_file_to_compressed_archive(file_path, dest_folder, filename)

                # Full path for the archive in the destination directory
                archive_path = os.path.join(dest_folder, f"{filename}.zip")

                #shutil.make_archive(os.path.join(dest_dir, archive_name), 'zip', source_dir)
                #print(f"Moved {filename} from {src_folder} to {dest_folder}")
                print(f"Archived file: {filename} from {src_folder} to {dest_folder}" +utils.utilities.get_path_separator() +filename+"" )
                
                #sql = """INSERT INTO archival_history (uuid, file_name, source_path, archive_path, archived_at) VALUES (%s, %s, %s, %s)"""
                random_uuid_str = str(random_uuid)
                values = (random_uuid_str, filename, src_folder, archive_path, date.today() )

                mod_mariadb.insert_archival_history(connection,values)


                    # Log to database
                # cursor.execute('''INSERT INTO file_archive (file_name, source_path, archive_path, archived_at)
                # VALUES (?, ?, ?, ?)''',
                # (filename, src_folder, dest_folder, datetime.now()))
               
                # cursor.execute(sql, values)

                # connection.commit()
                
            except Exception as e:
                print(f"Error moving file {filename}: {e}")

    #Zip % compress all the files presend in the dest_folder
    #logic not required since the files are getting compressed using 
    try:
        print(f"Compressing files at dest_folder : {dest_folder}") 
        utils.zip_and_compress.zip_uncompressed_files(dest_folder)
    except Exception as e:
                print(f"Error in zip and compress file in folder : {dest_folder}: {e}")


 


# Main function to move files for each folder based on configuration
def process_folders_using_db(config, records):
    print("\n\nProcessing folder starts..................................... " ) 
    
    #random uuid per run.
    namespace = uuid.NAMESPACE_DNS
    #random_uuid = uuid.uuid5()
    random_uuid = uuid.uuid5(namespace, 'dbs.com')


    archive_data=[]
    for record in records:
        print("record   ",record  ) 
        # print("record 0::  ",record[1]  ) 
        

        #Move files to archive (older than archive_days)
        print(f"\n<<< Processing DATA FOLDER >>>>...")
        move_files(random_uuid, config, record[2], record[3], record[5], connection)

        # print(f"\n<<< Processing ARCHIVE FOLDER >>>>...")
        # # Move files to delete (older than delete_days)
        # move_files( record[3], record[4], record[6] , connection)
 
        print(f"\n<<< END >>>>...\n")
    print("Processing folder ends "   ) 
 
 


def rollback_files(config, connection, filter_date):
   
    try:
        # Create a cursor
        cursor = connection.cursor(dictionary=True)  # Use dictionary=True for results as dicts
        
        # Define the SQL query
        sql = """
        SELECT id, file_name, source_path, archive_path, archived_at
        FROM file_archive
        WHERE archived_at = %s
        """
        
        # Execute the query with the filter date
        cursor.execute(sql, (filter_date,))
        
        # Fetch all matching records
        records = cursor.fetchall()

        #handle deleted files to archive directory first 
        print("\n>>> ROLLBACK DELETED FILES ")
        for record in records:
            print("file_name: "+record['file_name']+"\tsource_path: "+record['source_path']+"\t archive_path:"+record['archive_path'])
 

            if 'delete/'  in record['archive_path']: 
                #src_file = ""+ record['archive_path']+record['file_name'];
                #dest_file = ""+  record['source_path']+record['file_name'];
                src_file = f"{record['archive_path']}/{record['file_name']}"
                dest_file = f"{record['source_path']}/{record['file_name']}"

                print("src_file: "+src_file + "\t dest_file:"+dest_file)
               
                try:
                     shutil.move(src_file, dest_file)
                except FileNotFoundError:
                    return f"Error: The file '{src_file}' was not found."
                except Exception as e:
                    # Handle other potential exceptions
                    return f"An unexpected error occurred: {e}"


        #handle deleted files to archive directory first 
        print("\n>>> ROLLBACK ARCHIVE FILES ")
        for record in records:
            print("file_name: "+record['file_name']+"\tsource_path: "+record['source_path']+"\t archive_path:"+record['archive_path'])

            if 'archive/'  in record['archive_path']: 
                #src_file = ""+ record['archive_path']+record['file_name'];
                #dest_file = ""+  record['source_path']+record['file_name'];
                src_file = f"{record['archive_path']}/{record['file_name']}"
                dest_file = f"{record['source_path']}/{record['file_name']}"

                print("src_file: "+src_file + "\t dest_file:"+dest_file)
                try:
                     shutil.move(src_file, dest_file)
                except FileNotFoundError:
                    return f"Error: The file '{src_file}' was not found."
                except Exception as e:
                    # Handle other potential exceptions
                    return f"An unexpected error occurred: {e}"

        return records
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    
    finally:
        cursor.close()

def list_files(config):
    return 
 

# def archive_files():
#     # Load configuration from YAML
#     config = load_config()

#     # Connect to the MySQL database
#     # connection = connect_to_mysql(config)
#     connection1 = connect_to_mariadb(config)
#     # If connection was successful, fetch and print some information
#     if connection:

#         cursor = connection.cursor()
#         cursor.execute("SELECT DATABASE();")
#         db_info = cursor.fetchone()
#         print(f"You're connected to the database: {db_info[0]}")
    
#         #create table if not exists
#         create_table_if_not_exists(connection)

#         # Process the folders based on the configuration
#         process_folders(config, connection)

#          # Process the folders based on the configuration
#         date_filter = datetime.strptime("2024-12-20", "%Y-%m-%d").date()  # Ensure correct format
#         #rollback_files(config, connection,date_filter)
    
#         # Close the connection
#         cursor.close()
#         connection.close()
#         print("MySQL connection is closed.")

def rollback_archived_files(connection, records):
    # Load configuration from YAML
    config = load_config()

    # # Connect to the MySQL database
    # connection = connect_to_mysql(config)
    print(f"records ::::::: {records}") 
    # If connection was successful, fetch and print some information
    if records:
        for record in records:
            print(f"UUID :: {record[5]}")   
            print(f"Batch Name :: {record[4]}")  
            #def move_and_unzip_file(src_zip_path, dest_dir):
            utils.zip_and_compress.move_and_unzip_file(record[5], record[4])
    print(f"records ::::::: {records}") 

if __name__ == "__main__":

    """Main function to handle command-line arguments and invoke appropriate actions."""
    parser = argparse.ArgumentParser(description="File Archival System")
    parser.add_argument('--archive', action='store_true', help="Archive files from source directories to their corresponding archive folders")
    parser.add_argument('--listfiles', action='store_true', help="List files information from the directory to be archived")
    parser.add_argument('--rollback', action='store_true', help="Rollback archived files to their original locations")
    parser.add_argument('--rollingfolders', action='store_true', help="Rolling folders for configured days")
 
    # UUID argument as optional
    parser.add_argument('--uuid', type=str, help="UUID to associate with the rollback operation (optional)")
    
    #setting up logger
    #setup_logging()  
    #logging.debug(f"Logging set....")

    args = parser.parse_args()
    print(f"You're connected to the database: {args}")
   

    if args.archive:
        #logging.debug("Option selected: archive")

        # Load configuration from YAML
        config = load_config()

        connection = mod_mariadb.connect_to_mariadb(config)
        #create_table_if_not_exists(connection)
        records = mod_mariadb.get_all_archival_config_items(connection)
        

        # Process the folders based on the configuration
        process_folders_using_db(config, records)

         # Process the folders based on the configuration
        date_filter = datetime.strptime("2024-12-20", "%Y-%m-%d").date()  # Ensure correct format
        #rollback_files(config, connection,date_filter)
    
        # Close the connection
        #cursor.close()
        connection.close()
        print("Database connection is closed.")

        #archive_files()

        #archive_files()
    elif args.listfiles:
        logging.debug("Option selected: listfiles")
        list_files()
    elif args.rollback:
        print("Rollback 1")
        # Add the UUID argument
       

        if args.uuid:
            # If UUID is provided, validate and use it for rollback
            try:
                user_uuid = uuid.UUID(args.uuid)  # Validate the UUID format
                print(f"Rolling back with UUID: {user_uuid}")
            except ValueError:
                print(f"Error: The UUID provided '{args.uuid}' is invalid.")
                #return  # Exit the program if the UUID is invalid
        else:
            # If UUID is not provided, perform the rollback without UUID
            print("Rolling back without UUID.")

        # Set up argument parser to accept the UUID as a command-line argument
        # parser = argparse.ArgumentParser(description="Fetch records by UUID from archival_history table.")
        print("Rollback 2")
        parser.add_argument("uuid", help="The UUID to search for in the database (e.g., 123e4567-e89b-12d3-a456-426614174000)")
        print("Rollback 3")
        # Parse the arguments
     
        print("Rollback 4")
        # Convert the provided UUID argument to a UUID object
        try:
            record_uuid = uuid.UUID(args.uuid)
            uuid_str = str(args)
            
            # uuid5 = uuid.uuid5(uuid.NAMESPACE_DNS, 'dbs.com')
            # record_uuid =  uuid5.UUID(args, version=5)
            
        except ValueError:
            print("Invalid UUID format. Please provide a valid UUID.")
 

        # Load configuration from YAML
        config = load_config()

        connection = mod_mariadb.connect_to_mariadb(config)
        #create_table_if_not_exists(connection)
        records = mod_mariadb.get_all_archival_history_items(connection, record_uuid)

        logging.debug("Option selected: rollback")
        rollback_archived_files(connection, records)

        connection.close()
        print("Database connection is closed.")
    elif args.rollingfolders:
         # Load configuration from YAML
        config = load_config()

        utils.file_utils.manage_folders(config)
    else:
        logging.debug("No valid option selected. Displaying help.")
        parser.print_help()
    
