import mysql.connector
from mysql.connector import Error
import yaml
import logging

# Load YAML configuration file
def load_config():
    with open('file_config.yaml', 'r') as file:
        return yaml.safe_load(file)
    

logger = logging.getLogger(__name__)
logger.info(f"Logging set....")

# Function to establish a connection to the MySQL database
def connect_to_mysql(config):

    try:
        database_config = config['mysql']
        logger.info(f"database_config: {database_config}")
        # Create a connection to the database
        connection = mysql.connector.connect(
            host=database_config['host'],
            user=database_config['user'],
            port=database_config['port'],
            password=database_config['password'],
            database=database_config['database']
        )
        logger.info("Successfully connected to the MySQL database!")
        return connection
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        exit(1)
        return None
    
    
def connect_to_mariadb(config):

    connection = None  # Initialize connection to None

    try:
        database_config = config['mariadb']
        logger.info(f"database_config: {database_config}")
        # Create a connection to the database
        connection = mysql.connector.connect(
            host=database_config['host'],
            user=database_config['user'],
            port=database_config['port'],
            password=database_config['password'],
            database=database_config['database']
        )

        if connection.is_connected():
            logger.info("Connected to MariaDB successfully!")
            
            # Fetch and display server information
            db_info = connection.get_server_info()
            logger.info(f"MariaDB Server Version: {db_info}")

            # Example query
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            current_db = cursor.fetchone()
            logger.info(f"Currently connected to database: {current_db}")

    except Error as e:
        logger.error(f"Error while connecting to MariaDB: {e}")
        exit(1)
    finally:
        # Ensure the connection is closed
        #if connection.is_connected():
        return connection
 


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
        logger.info("Table 'file_archive' is ready (created if not exists).")
    except mysql.connector.Error as err:
        logger.error(f"Error while creating table: {err}")
    finally:
        cursor.close()

def get_archival_config_items(connection):
    cursor = connection.cursor()

    # SQL query to create a table if it doesn't exist
    select_query = '''
    SELECT 
        ID, 
        batch_name, 
        data_folder, 
        archive_folder, 
        delete_folder, 
        archival_period, 
        delete_period, 
        is_Active,
        email_receipt, 
        created_by, 
        created_on 
        FROM 
        archival_config order by ID;

    '''
    try:
        cursor.execute(select_query)
        records = cursor.fetchall()
        logger.info("Fetched records from archival_config table :")

        # Fetch column names
        columns = [column[0] for column in cursor.description]

        records_array = []
 
        logger.info("Records stored in array:")
        logger.info("Total Records ", records)
        logger.info("Total Records ", len(records))
        
        #return records_array 
        return records
    
    except mysql.connector.Error as err:
        logger.error(f"Error while select records from table archival_config: {err}")
    finally:
        cursor.close()


def get_all_file_archive(connection, filter_date):
     
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
        return records
    except mysql.connector.Error as err:
        logger.error(f"Error while select records from table archival_config: {err}")
    finally:
        cursor.close()

def get_all_archival_batch_items(connection):
    cursor = connection.cursor()

    # SQL query to create a table if it doesn't exist
    select_query = '''
    SELECT 
        ID, 
        uuid, 
        batch_name, 
        data_folder, 
        archive_folder, 
        delete_folder, 
        archive_days, 
        delete_days, 
        is_Active,
        email_receipt, 
        created_by, 
        created_on 
        FROM 
        archival_history ;

    '''
    try:
        cursor.execute(select_query)
        records = cursor.fetchall()
        logger.info("Fetched records:")

        # Fetch column names
        columns = [column[0] for column in cursor.description]

        records_array = []
 
        # Print the array
        logger.info("Records stored in array:")
        logger.info("Total Records ", records)
        logger.info("Total Records ", len(records))
        
        #return records_array 
        return records
    
    except mysql.connector.Error as err:
        logger.error(f"Error while select records from table archival_batch_items: {err}")
    finally:
        cursor.close()

def get_all_archival_history_items(connection):
    cursor = connection.cursor()

    # Ensure that the UUID is converted to string for the query
    #record_uuid_str = str(record_uuid)  # Convert UUID object to string if not already

    # SQL query with WHERE clause to filter by UUID
    # SELECT id, uuid, batch_name, file_name, source_path, archive_path, archived_at
    # FROM archival_history
    # WHERE uuid = %s

    # SQL query with WHERE clause to filter by lastest ID
    query = """

    SELECT id, uuid, batch_name, file_name, source_path, archive_path, archived_at
    FROM archival_history
    WHERE  UUID= (   
        SELECT UUID
        FROM archival_history
        ORDER BY id DESC
    LIMIT 1);
    """

    try:
        # Execute the query with the provided UUID
        #cursor.execute(query, (record_uuid_str,))
        cursor.execute(query)
        
        # Fetch all matching records
        results = cursor.fetchall()  # Retrieve all matching records
        
        if results:
            logger.info(f"Found {len(results)} record(s) matching the UUID:")
            for record in results:
                logger.info(record)
            return results
        else:

            logger.info("No record found with the given UUID.")
            return None
    
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        return None
    
    finally:
        cursor.close()



def insert_archival_history(conn,  values):
 
    cursor = conn.cursor()
    query = """INSERT INTO archival_history (uuid, file_name, source_path, archive_path, archived_at) VALUES (%s, %s, %s, %s, %s)"""
 
    try:
        logger.info("SQL Query:", query)
        logger.info("SQL Values:", values)

        # Execute the query with the provided values
        cursor.execute(query, values)
        
        # Commit the transaction
        conn.commit()
        logger.info(f"Record inserted into archival_history successfully")
    
    except mysql.connector.Error as err:
        logger.error(f"Error: {err}")
        conn.rollback()  # Rollback in case of error
    
    finally:
        # Close the cursor
        cursor.close()

if __name__ == "__main__":
    config = load_config()
    connection = connect_to_mariadb(config)
    #create_table_if_not_exists(connection)
    records = get_archival_config_items(connection)
