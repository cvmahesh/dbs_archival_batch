import os
import shutil
import time
import yaml

# import mysql.connector
# from mysql.connector import Error

import logging
import yaml
import argparse
from datetime import datetime

 
import dao.dao_mariadb 
import utils.zip_and_compress
import utils.file_utils
import utils.utilities
import uuid
import batch_logger.archival_logger
from   archival_error.ErrorLogger import ErrorLogger
import dao.dao_mariadb 
 

error_logger = ErrorLogger()
ignorelist = []
processed_dir_list=[] 

# Load YAML configuration file
def load_config():
    try:
        config_file_path = os.path.join(os.path.dirname(__file__), 'config/archival_batch_config.yaml')
        with open(config_file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        logger.error(f"Error in loading prop file file_config.yaml : {e}")
        exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error: Failed to parse the YAML file. Details: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error while loading the configuration file: {e}")
        exit(1)

# Function to move files based on age.
# logic is to consider all subdirectories under the directory configured in database table archival_config
# folders mentioned in the yaml config file will be skipped. <<ignore_dirs>>
def archive_files(random_uuid, config, src_folder, dest_folder, age_days, connection):
    filename=""
    file_path=""

    logger.info(f"archive_files called...   ")

    current_time = time.time()
    
    logger.debug(f".....src_folder from DB config: {src_folder}")
    logger.debug(f".....dest_folder from DB config: {dest_folder}")
    

    src_folder = config['source_base_dir'] + src_folder 
    dest_base_dir= config['dest_base_dir']
    ignore_dirs = config['ignore_dirs']
    dest_new_dir = utils.utilities.get_folder_name_from_system_date() +utils.utilities.get_path_separator()+dest_folder
    dest_folder = dest_base_dir + dest_new_dir
    #config['dest_base_dir'] + utils.utilities.get_folder_name_from_system_date() +utils.utilities.get_path_separator()+dest_folder

    #Get all subdirectories under base
    subdirs = utils.file_utils.find_all_subdirectories(src_folder)
    logger.debug(".....Subdirectories:")
    logger.debug(f".....new src_folder: {src_folder}")
    logger.debug(f".....new dest_base_dir: {dest_base_dir}")
    logger.debug(f".....dest_new_dir: {dest_new_dir}")
    logger.debug(f".....dest_folder: {dest_folder}")
    logger.debug(f".....ignore_dirs: {ignore_dirs}")
    logger.debug(f".....age_days: {age_days}")
    logger.debug(f"\n.....Finding Subdirectories under :{subdirs}")
    # for subdir in subdirs:
    #     #dest_new_dir = dest_base_dir +utils.utilities.get_folder_name_from_system_date() +utils.utilities.get_path_separator()+ subdir
    #     dest_new_dir = dest_folder +utils.utilities.get_path_separator()+ subdir
    #     src_new_dir = src_folder+utils.utilities.get_path_separator()+subdir
    #     print(src_new_dir+"...."+dest_new_dir)

    logger.info(f"\n.....Archival starting for subdirectories under :{src_folder}")
    for subdir in subdirs:
        dest_new_dir = dest_folder +utils.utilities.get_path_separator()+ subdir
        src_new_dir = src_folder+utils.utilities.get_path_separator()+subdir
        logger.debug("DIRECTORY Processing...."+subdir+"....under....."+src_new_dir+"....to...."+dest_new_dir)
        
        # Check if the directory is in the ignore list
        if any(os.path.abspath(src_new_dir).startswith(os.path.abspath(ignore)) 
            for ignore in ignore_dirs):
                logger.info(f"Skipping: {src_new_dir} (in ignore_dirs)")
                ignorelist.append(src_new_dir)
                continue
                
        
        # Skipping dirs that are already processed
        if src_new_dir in processed_dir_list:
            logger.debug("############################################")
            logger.info(f"Skipping {src_new_dir}: Already processed.")
            logger.debug("############################################")
        else:
            #Adding to processed dir list to check at later stage
            processed_dir_list.append(src_new_dir);
    
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
                                logger.info(f"Moving file from {file_path} to {dest_path}  " )
                                utils.zip_and_compress.tar_and_gzip(file_path, filename, dest_new_dir)
                                archive_path = os.path.join(dest_new_dir, f"{filename}.tar.gz")
                                logger.info(f"Archived file: {filename} from {src_new_dir} to {archive_path}"   )
                                
                                #sql = """INSERT INTO archival_history (uuid, file_name, source_path, archive_path, archived_at) VALUES (%s, %s, %s, %s)"""
                                random_uuid_str = str(random_uuid)
                                values = (random_uuid_str, filename, src_new_dir, archive_path, datetime.now() )
                                dao.dao_mariadb.insert_archival_history(connection,values)
                            except Exception as e:
                                logger.error(f"Error <<<1>>>> moving file {file_path}: {e}")
                                error_logger.log_error(f"{file_path}",e)
                                continue
                        else:
                            logger.debug(f"Skipping...Not aged for archival....{file_path}")
                
            
            except FileNotFoundError as e:
                logger.error(f"<<<1>>>>FileNotFoundError: {e}")
                error_logger.log_error(f"{file_path}",e)
            except Exception as e:
                logger.error(f"<<<1>>>>An unexpected Exception occurred: {e}")
                error_logger.log_error(f"{file_path}",e)

    try:
         # Clean the directory by deleting files and directories that aren't in the last n days
        #dest_base_dir = r"C:\\workspace\\testing\\RollingFolders"  
        delete_dirs_days = config['delete_dirs_days'] 
        last_n_days = utils.file_utils.get_last_n_days(delete_dirs_days)
        logger.debug(f"last_n_days:{last_n_days}")
        logger.debug(f"dest_base_dir:{dest_base_dir}")
        utils.file_utils.clean_directory(dest_base_dir, last_n_days)
    except Exception as e:
            logger.error(f"Exception occurred in calling utils.file_utils.clean_directory: {e}")
            error_logger.log_error(f"{file_path}",e)

   

# Main function to move files for each folder based on configuration
def archive_folders(config, records):
    logger.info("\n\nProcessing folder starts..................................... " ) 
    
    logger.debug("config config   "  )
    logger.debug("config   ",config  )
    logger.debug("config config   "  )

    #random uuid per run.
    namespace = uuid.NAMESPACE_DNS
    random_uuid = uuid.uuid1()
    #random_uuid = uuid.uuid5(namespace, 'dbs.com')


    archive_data=[]
    for record in records:
        #logger.debug("record   ",record  ) 
        print("record 0::  ",record[1]  ) 
        

        #Move files to archive (older than archive_days)
        logger.debug(f"\n\n<<< Processing DATA FOLDER starts for >>>>...")
        logger.debug(f"src_folder...{record[2]}")
        logger.debug(f"dest_folder...{record[3]}")
          
        archive_files(random_uuid, config, record[2], record[3], record[5], connection)
        # def archive_files(random_uuid, config, src_folder, dest_folder, age_days, connection):
        logger.debug(f"\n<<< Processing DATA FOLDER ends for {record[2]}>>>>...\n\n")
        # print(f"\n<<< Processing ARCHIVE FOLDER >>>>...")
        # # Move files to delete (older than delete_days)
        # move_files( record[3], record[4], record[6] , connection)
 
    print("Processing folder ends "   ) 
 
 


# def rollback_files(config, connection, filter_date):
   
#     try:
 
#         records = dao.dao_mariadb.get_all_file_archive(connection, filter_date)

#         #handle deleted files to archive directory first 
#         logger.info("\n>>> ROLLBACK DELETED FILES ")
#         for record in records:
#             logger.info("file_name: "+record['file_name']+"\tsource_path: "+record['source_path']+"\t archive_path:"+record['archive_path'])
 

#             if 'delete/'  in record['archive_path']: 
#                 #src_file = ""+ record['archive_path']+record['file_name'];
#                 #dest_file = ""+  record['source_path']+record['file_name'];
#                 src_file = f"{record['archive_path']}/{record['file_name']}"
#                 dest_file = f"{record['source_path']}/{record['file_name']}"

#                 logger.info("src_file: "+src_file + "\t dest_file:"+dest_file)
               
#                 try:
#                      shutil.move(src_file, dest_file)
#                 except FileNotFoundError:
#                     return f"Error: The file '{src_file}' was not found."
#                 except Exception as e:
#                     # Handle other potential exceptions
#                     return f"An unexpected error occurred: {e}"


#         #handle deleted files to archive directory first 
#         logger.info("\n>>> ROLLBACK ARCHIVE FILES ")
#         for record in records:
#             logger.info("file_name: "+record['file_name']+"\tsource_path: "+record['source_path']+"\t archive_path:"+record['archive_path'])

#             if 'archive/'  in record['archive_path']: 
#                 #src_file = ""+ record['archive_path']+record['file_name'];
#                 #dest_file = ""+  record['source_path']+record['file_name'];
#                 src_file = f"{record['archive_path']}/{record['file_name']}"
#                 dest_file = f"{record['source_path']}/{record['file_name']}"

#                 logger.info("src_file: "+src_file + "\t dest_file:"+dest_file)
#                 try:
#                      shutil.move(src_file, dest_file)
#                 except FileNotFoundError:
#                     return f"Error: The file '{src_file}' was not found."
#                 except Exception as e:
#                     # Handle other potential exceptions
#                     return f"An unexpected error occurred: {e}"

#         return records
    
#     except Exception as err:
#         logger.error(f"Error: {err}")
#         return []
    
 

def list_files(config):
    return 
 
 

def rollback_archived_files(connection, records):
    # Load configuration from YAML
    config = load_config()

    # # Connect to the MySQL database
    # connection = connect_to_mysql(config)
    logger.debug(f"records ::::::: {records}") 
    # If connection was successful, fetch and print some information
    if records:
        for record in records:
            logger.info(f"rollback_archived_files:src_tar.gz_path :: {record[5]}")   
            logger.info(f"rollback_archived_files:dest_dir Name :: {record[4]}")  
            #def move_and_unzip_file(src_zip_path, dest_dir):
           
            
            try:
                #utils.zip_and_compress.move_and_unzip_file(record[5], record[4])
                utils.zip_and_compress.uncompress_tar_gz(record[5], record[4])
                
            except Exception as e:
                logger.error("Error in utils.zip_and_compress.uncompress_tar_gz :: {e}")


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
    batch_logger.archival_logger.setup_logging()  
    logger = logging.getLogger(__name__)
    logger.info(f"Logging set....")

    args = parser.parse_args()
 
   

    if args.archive:
        try:
            logger.debug("Option selected: archive")

            # Load configuration from YAML
            logger.debug("Loading config.....")
            config = load_config()

            logger.debug("Connection obj for database.....")
            connection = dao.dao_mariadb.connect_to_mariadb(config)
            if connection is None:
                logger.error("Exiting program. Database Connection object is null")
                exit(1)

            logger.debug("get_archival_config_items.....")
            records = dao.dao_mariadb.get_archival_config_items(connection)
            
            # Archive the folders based on the configuration in database
            logger.debug("archive_folders.....")
            archive_folders(config, records)
        
            # Close the connection
            logger.debug("Closing connection")
            connection.close()
            logger.debug("Database connection is closed.")




            logger.debug("Printing All Errors")
            status = error_logger.print_errors()
            logger.debug("Archival process completed. Program exit with status 0")
            for ignore_item in ignorelist:
                logger.debug(f"ignore_item: {ignore_item}")
            for processed_dir in processed_dir_list:
                logger.debug(f"processed_dir: {processed_dir}")

            #error_logger.print_errors()  
            exit(status)
            #Exit with 1 if archival_error.ErrorLo
        except Exception as e:
            logger.error("Error in args.archive:: {e}")
            exit(1)
        
    elif args.listfiles:
        try: 
            logger.debug("Option selected: listfiles")
            list_files()
            logger.debug("Listed files. Program exit with status 0")
  
        except Exception as e:
            logger.error("Error in args.listfiles:: {e}")
            exit(1)
    elif args.rollback:
        try:
            logger.debug("Option selected: rollback")
            # Add the UUID argument
            # Load configuration from YAML
            logger.debug("Loading config.....")
            config = load_config()

            logger.debug("Connection obj for database.....")
            connection = dao.dao_mariadb.connect_to_mariadb(config)
            if connection is None:
                logger.error("Exiting program. Database Connection object is null")
                exit(1)

            #create_table_if_not_exists(connection)
            logger.debug("get_all_archival_history_items.....")
            records = dao.dao_mariadb.get_all_archival_history_items(connection)

            logger.debug("rollback_archived_filesk")
            rollback_archived_files(connection, records)

            logger.debug("Closing connection")
            connection.close()

            logger.debug("Rollback completed. Program exit with status 0")
        except Exception as e:
            logger.error("Error in args.rollback:: {e}")
            exit(1)
       
 
    else:
        logger.debug("No valid option selected. Displaying help.")
        parser.print_help()
    
    logger.debug("Exiting progream with status 0")
    exit(0)
    
