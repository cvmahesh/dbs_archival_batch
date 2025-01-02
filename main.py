import os
import shutil
import time
import yaml
# from   datetime import datetime, timedelta
import mysql.connector
import logging
import yaml
# import sys
# from  datetime import date
import argparse
from mysql.connector import Error
from datetime import datetime

 
import sql.mod_mariadb 
import utils.zip_and_compress
import utils.file_utils
import utils.utilities
import uuid
import logger.archival_logger
from   archival_error.ErrorLogger import ErrorLogger

error_logger = ErrorLogger()

# Load YAML configuration file
def load_config():
    try:
        config_file_path = os.path.join(os.path.dirname(__file__), 'config/archival_batch_config.yaml')
        with open(config_file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        print(f"Error in loading prop file file_config.yaml : {e}")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse the YAML file. Details: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error while loading the configuration file: {e}")
        exit(1)

# Function to move files based on age.
# logic is to consider all subdirectories under the directory configured in database table archival_config
# folders mentioned in the yaml config file will be skipped. <<ignore_dirs>>
def archive_files(random_uuid, config, src_folder, dest_folder, age_days, connection):
    filename=""
    file_path=""

    print(f"archive_files called...   ")

    current_time = time.time()
    
    print(f".....src_folder from DB config: {src_folder}")
    print(f".....dest_folder from DB config: {dest_folder}")
    

    src_folder = config['source_base_dir'] + src_folder 
    dest_base_dir= config['dest_base_dir']
    ignore_dirs = config['ignore_dirs']
    dest_new_dir = utils.utilities.get_folder_name_from_system_date() +utils.utilities.get_path_separator()+dest_folder
    dest_folder = dest_base_dir + dest_new_dir
    #config['dest_base_dir'] + utils.utilities.get_folder_name_from_system_date() +utils.utilities.get_path_separator()+dest_folder


    #Get all subdirectories under base
    subdirs = utils.file_utils.find_all_subdirectories(src_folder)
    print(".....Subdirectories:")
    print(f".....new src_folder: {src_folder}")
    print(f".....new dest_base_dir: {dest_base_dir}")
    print(f".....dest_new_dir: {dest_new_dir}")
    print(f".....dest_folder: {dest_folder}")
    print(f".....ignore_dirs: {ignore_dirs}")
    print(f".....age_days: {age_days}")
    print(f"\n.....Finding Subdirectories under :{subdirs}")
    # for subdir in subdirs:
    #     #dest_new_dir = dest_base_dir +utils.utilities.get_folder_name_from_system_date() +utils.utilities.get_path_separator()+ subdir
    #     dest_new_dir = dest_folder +utils.utilities.get_path_separator()+ subdir
    #     src_new_dir = src_folder+utils.utilities.get_path_separator()+subdir
    #     print(src_new_dir+"...."+dest_new_dir)

    print(f"\n.....Archival starting for subdirectories under :{src_folder}")
    for subdir in subdirs:
        dest_new_dir = dest_folder +utils.utilities.get_path_separator()+ subdir
        src_new_dir = src_folder+utils.utilities.get_path_separator()+subdir
        print("DIRECTORY Processing...."+subdir+"....under....."+src_new_dir+"....to...."+dest_new_dir)
        
        # Check if the directory is in the ignore list
        if any(os.path.abspath(src_new_dir).startswith(os.path.abspath(ignore)) 
            for ignore in ignore_dirs):
                print(f"Skipping: {src_new_dir} (in ignore_dirs)")
                continue

        try:
            # Iterate through files in the source folder
            for filename in os.listdir(src_new_dir):
                
                    file_path = os.path.join(src_new_dir, filename)
                    dest_path = os.path.join(dest_new_dir, filename)
                    #print("Checking...."+file_path+"......")
                    # Skip if it's not a file
                    if not os.path.isfile(file_path):
                        #print(f"Skipping: {file_path} as this is directory")
                        continue
                    
                    # Get the file's last modified time
                    file_mod_time = os.path.getmtime(file_path)
                    file_age_days = (current_time - file_mod_time) / (60 * 60 * 24)
                    
                    # If the file is older than the threshold, move it
                    if file_age_days >= age_days:
                        
                        try:
                            print(f"Moving file from {file_path} to {dest_path}  " )
                            utils.zip_and_compress.tar_and_gzip(file_path, filename, dest_new_dir)
                            archive_path = os.path.join(dest_new_dir, f"{filename}.tar.gz")
                            print(f"Archived file: {filename} from {src_new_dir} to {archive_path}"   )
                            
                            #sql = """INSERT INTO archival_history (uuid, file_name, source_path, archive_path, archived_at) VALUES (%s, %s, %s, %s)"""
                            random_uuid_str = str(random_uuid)
                            values = (random_uuid_str, filename, src_new_dir, archive_path, datetime.now() )
                            sql.mod_mariadb.insert_archival_history(connection,values)
                        except Error as e:
                            print(f"Error <<<1>>>> moving file {file_path}: {e}")
                            error_logger.log_error(f"{file_path}",e)
                            continue
                    else:
                        print(f"Skipping...Not aged for archival....{file_path}")

        except FileNotFoundError as e:
            print(f"<<<1>>>>FileNotFoundError: {e}")
            error_logger.log_error(f"{file_path}",e)
        except Exception as e:
            print(f"<<<1>>>>An unexpected Exception occurred: {e}")
            error_logger.log_error(f"{file_path}",e)
        except Error as e:
            print(f"<<<1>>>> Error  <<<2>>>> moving file {file_path}: {e}")
            error_logger.log_error(f"{file_path}",e)

    # Clean the directory by deleting files and directories that aren't in the last n days
    #dest_base_dir = r"C:\\workspace\\testing\\RollingFolders"  
    delete_dirs_days = config['delete_dirs_days'] 
    last_n_days = utils.file_utils.get_last_n_days(delete_dirs_days)
    print(f"last_n_days:{last_n_days}")
    utils.file_utils.clean_directory(dest_base_dir, last_n_days)

# Main function to move files for each folder based on configuration
def archive_folders_using_db(config, records):
    print("\n\nProcessing folder starts..................................... " ) 
    
    print("config config   "  )
    print("config   ",config  )
    print("config config   "  )

    #random uuid per run.
    namespace = uuid.NAMESPACE_DNS
    random_uuid = uuid.uuid1()
    #random_uuid = uuid.uuid5(namespace, 'dbs.com')


    archive_data=[]
    for record in records:
        print("record   ",record  ) 
        # print("record 0::  ",record[1]  ) 
        

        #Move files to archive (older than archive_days)
        print(f"\n<<< Processing DATA FOLDER >>>>...")
        print(f"src_folder...{record[2]}")
        print(f"dest_folder...{record[3]}")
        print(f"\n<<< Processing DATA FOLDER >>>>...")


            
        archive_files(random_uuid, config, record[2], record[3], record[5], connection)
        # def archive_files(random_uuid, config, src_folder, dest_folder, age_days, connection):
        
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
 
 

def rollback_archived_files(connection, records):
    # Load configuration from YAML
    config = load_config()

    # # Connect to the MySQL database
    # connection = connect_to_mysql(config)
    print(f"records ::::::: {records}") 
    # If connection was successful, fetch and print some information
    if records:
        for record in records:
            print(f"rollback_archived_files:src_tar.gz_path :: {record[5]}")   
            print(f"rollback_archived_files:dest_dir Name :: {record[4]}")  
            #def move_and_unzip_file(src_zip_path, dest_dir):
           
            
            try:
                #utils.zip_and_compress.move_and_unzip_file(record[5], record[4])
                utils.zip_and_compress.uncompress_tar_gz(record[5], record[4])
                
            except Error:
                print("Error in utils.zip_and_compress.uncompress_tar_gz :: {Error}")

    print(f"records ::::::: {records}") 

if __name__ == "__main__":

    """Main function to handle command-line arguments and invoke appropriate actions."""
    parser = argparse.ArgumentParser(description="File Archival System")
    parser.add_argument('--archive', action='store_true', help="Archive files from source directories to their corresponding archive folders")
    parser.add_argument('--listfiles', action='store_true', help="List files information from the directory to be archived")
    parser.add_argument('--rollback', action='store_true', help="Rollback archived files to their original locations")
    # parser.add_argument('--rollingfolders', action='store_true', help="Rolling folders for configured days")
 
    # UUID argument as optional
    parser.add_argument('--uuid', type=str, help="UUID to associate with the rollback operation (optional)")
    
    #setting up logger
    logger.archival_logger.setup_logging()  
    logger = logging.getLogger(__name__)
    logging.info(f"Logging set....")

    args = parser.parse_args()
 
   

    if args.archive:
        logging.debug("Option selected: archive")

        # Load configuration from YAML
        config = load_config()

        connection = sql.mod_mariadb.connect_to_mariadb(config)
        if connection is None:
            logging.error("Exiting program. Database Connection object is null")
            exit(1)

        records = sql.mod_mariadb.get_archival_config_items(connection)
        
        # Archive the folders based on the configuration in database
        archive_folders_using_db(config, records)
    
        # Close the connection
        connection.close()
        print("Database connection is closed.")


        
        print("Printing All Errors")
        status = error_logger.print_errors()
        print("Archival process completed")
        
        #Exit with 1 if archival_error.ErrorLogger.print_errors() have records 
        exit(status)

    elif args.listfiles:
        logging.debug("Option selected: listfiles")
        list_files()
    elif args.rollback:
        logging.debug("Option selected: rollback")
        # Add the UUID argument
        # Load configuration from YAML
        config = load_config()

        connection = sql.mod_mariadb.connect_to_mariadb(config)
        if connection is None:
            logging.error("Exiting program. Database Connection object is null")
            exit(1)

        #create_table_if_not_exists(connection)
        records = sql.mod_mariadb.get_all_archival_history_items(connection)

        logging.debug("Option selected: rollback")
        rollback_archived_files(connection, records)

        connection.close()
        print("Database connection is closed.")
 
    else:
        logging.debug("No valid option selected. Displaying help.")
        parser.print_help()
    
    print("Exiting progream with status 0")
    exit(0)
    
