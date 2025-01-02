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
import mod_mariadb 

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
def move_files(src_folder, dest_folder, age_days, connection):
    current_time = time.time()
    
    print(f"Move from {src_folder} to {dest_folder}")

    cursor = connection.cursor()


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
                shutil.move(file_path, dest_path)
                print(f"Moved {filename} from {src_folder} to {dest_folder}")
                print(f"Archived file: {filename} from {src_folder} to {dest_folder}" +"\t" +filename+"\t" +src_folder+"\t" +dest_folder+"\t")
                
                sql = """INSERT INTO file_archive (file_name, source_path, archive_path, archived_at) VALUES (%s, %s, %s, %s)"""
                values = (filename, src_folder, dest_folder, date.today() )

                print("SQL Query:", sql)
                print("Values:", values)

                    # Log to database
                # cursor.execute('''INSERT INTO file_archive (file_name, source_path, archive_path, archived_at)
                # VALUES (?, ?, ?, ?)''',
                # (filename, src_folder, dest_folder, datetime.now()))
               
                cursor.execute(sql, values)

                connection.commit()
                
            except Exception as e:
                print(f"Error moving file {filename}: {e}")

# Main function to move files for each folder based on configuration
def process_folders(config, connection):
    for folder_name, folder_config in config['folders'].items():
        print(f"Processing {folder_name}...")

        print(f"\n<<< Processing DATA FOLDER >>>>...")
        # Move files to archive (older than archive_days)
        move_files(folder_config['data_folder'], folder_config['archive_folder'], folder_config['archive_days'], connection)

        print(f"\n<<< Processing ARCHIVE FOLDER >>>>...")
        # Move files to delete (older than delete_days)
        move_files(folder_config['archive_folder'], folder_config['delete_folder'], folder_config['delete_days'], connection)

        print(f"\n<<< END >>>>...\n")

 

# Function to establish a connection to the MySQL database
def connect_to_mysql(config):

    try:
        database_config = config['mysql']
        print(f"database_config: {database_config}")
        # Create a connection to the database
        connection = mysql.connector.connect(
            host=database_config['host'],
            user=database_config['user'],
            port=database_config['port'],
            password=database_config['password'],
            database=database_config['database']
        )
        print("Successfully connected to the MySQL database!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def connect_to_mariadb(config):

    try:
        connection = None  # Initialize connection to None
        database_config = config['mariadb']
        # Establish the connection
        print(f"mariadb database_config : {database_config}")
        connection =  mod_mariadb.connect_to_mariadb() 
            # host='localhost',       # Change to your host, e.g., '127.0.0.1' or a remote IP
            # user='root',       # Replace with your MariaDB username
            # password='Mar-1976',    # Replace with your MariaDB password
            # port='3307',
            # charset='utf8mb4',  # Use utf8mb4 for full Unicode support
            # database='batch_db'      # Replace with your MariaDB database name

        #     host=database_config['host'],
        #     user=database_config['user'],
        #     port=database_config['port'],
        #     #password=database_config['password'].encode("utf-8") ,
        #     password=database_config['password'],
        #     #charset='utf8mb4',  # Use utf8mb4 for full Unicode support
        #     #charset="utf8mb3",
        #     database=database_config['database']
            
        # )

        #if connection.is_connected():
        print("Connected to MariaDB successfully!")
        
        # Fetch and display server information
        #db_info = connection.get_server_info()
        #print(f"MariaDB Server Version: {db_info}")

        # Example query
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        current_db = cursor.fetchall()
        print(f"Currently connected to database: {current_db}")

    except Error  as e:
        print(f"Error while connecting to MariaDB: {e}")

    finally:
        # Ensure the connection is closed
        #if connection.is_connected():
        #connection.close()
        if connection:
            connection.close()
            print("MariaDB connection closed.")




def create_table_if_not_exists(connection):
    cursor = connection.cursor()

    # SQL query to create a table if it doesn't exist
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS file_archive (
        id INT AUTO_INCREMENT PRIMARY KEY,
        file_name VARCHAR(100),
        source_path VARCHAR(100),
        archive_path VARCHAR(100),
        archived_at DATE DEFAULT NULL
    );
    '''
    try:
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'file_archive' is ready (created if not exists).")
    except mysql.connector.Error as err:
        print(f"Error while creating table: {err}")
    finally:
        cursor.close()


def rollback_files(config, connection, filter_date):
    """
    Fetches records from the file_archive table based on the given date filter.

    Args:
        connection: MySQL database connection object.
        filter_date: The date to filter records (YYYY-MM-DD).

    Returns:
        List of records matching the date filter.
    """
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
 

def archive_files():
    # Load configuration from YAML
    config = load_config()

    # Connect to the MySQL database
    connection = connect_to_mysql(config)
    connection1 = connect_to_mariadb(config)
    # If connection was successful, fetch and print some information
    if connection:

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        db_info = cursor.fetchone()
        print(f"You're connected to the database: {db_info[0]}")
    
        #create table if not exists
        create_table_if_not_exists(connection)

        # Process the folders based on the configuration
        process_folders(config, connection)

         # Process the folders based on the configuration
        date_filter = datetime.strptime("2024-12-20", "%Y-%m-%d").date()  # Ensure correct format
        #rollback_files(config, connection,date_filter)
    
        # Close the connection
        cursor.close()
        connection.close()
        print("MySQL connection is closed.")

def rollback_archived_files():
    # Load configuration from YAML
    config = load_config()

    # Connect to the MySQL database
    connection = connect_to_mysql(config)

    # If connection was successful, fetch and print some information
    if connection:

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        db_info = cursor.fetchone()
        print(f"You're connected to the database: {db_info[0]}")
    
        #create table if not exists
        create_table_if_not_exists(connection)

        # Process the folders based on the configuration
        #process_folders(config, connection)

         # Process the folders based on the configuration
        date_filter = datetime.strptime("2024-12-20", "%Y-%m-%d").date()  # Ensure correct format
        rollback_files(config, connection,date_filter)
    
        # Close the connection
        cursor.close()
        connection.close()
        print("MySQL connection is closed.")

if __name__ == "__main__":

    """Main function to handle command-line arguments and invoke appropriate actions."""
    parser = argparse.ArgumentParser(description="File Archival System")
    parser.add_argument('--archive', action='store_true', help="Archive files from source directories to their corresponding archive folders")
    parser.add_argument('--listfiles', action='store_true', help="List files information from the directory to be archived")
    parser.add_argument('--write-details', metavar='FILE_PATH', help="Write archival details to a specified file")
    parser.add_argument('--rollback', action='store_true', help="Rollback archived files to their original locations")
 
    #setting up logger
    setup_logging() 
    logging.debug(f"Logging set....")

    args = parser.parse_args()

   

    if args.archive:
        logging.debug("Option selected: archive")
        archive_files()
        #archive_files()
    elif args.listfiles:
        logging.debug("Option selected: listfiles")
        list_files()
    elif args.write_details:
        logging.debug(f"Option selected: write-details to {args.write_details}")
        #write_archival_details_to_file(args.write_details)
    elif args.rollback:
        logging.debug("Option selected: rollback")
        rollback_archived_files()
    else:
        logging.debug("No valid option selected. Displaying help.")
        parser.print_help()
    
