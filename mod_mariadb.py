import mysql.connector
from mysql.connector import Error
import yaml


# Load YAML configuration file
def load_config():
    with open('file_config.yaml', 'r') as file:
        return yaml.safe_load(file)
    



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

    connection = None  # Initialize connection to None

    try:
        database_config = config['mariadb']
        print(f"database_config: {database_config}")
        # Create a connection to the database
        connection = mysql.connector.connect(
            host=database_config['host'],
            user=database_config['user'],
            port=database_config['port'],
            password=database_config['password'],
            database=database_config['database']
        )
    

 

        if connection.is_connected():
            print("Connected to MariaDB successfully!")
            
            # Fetch and display server information
            db_info = connection.get_server_info()
            print(f"MariaDB Server Version: {db_info}")

            # Example query
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            current_db = cursor.fetchone()
            print(f"Currently connected to database: {current_db}")

    except Error as e:
        print(f"Error while connecting to MariaDB: {e}")

    finally:
        # Ensure the connection is closed
        #if connection.is_connected():
        return connection
        
            # connection.close()
            # print("MariaDB connection closed.")

# Run the program


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

def get_all_archival_batch_items(connection):
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
        archival_config ;

    '''
    try:
        cursor.execute(select_query)
        records = cursor.fetchall()
        print("Fetched records:")

        # Fetch column names
        columns = [column[0] for column in cursor.description]

        records_array = []

        # for record in records:
        #     print(f"ID: {record[0]}, batch_name: {record[1]}, data_folder: {record[2]}")

        #     records_array.append({
        #         "ID": record[0],
        #         "batch_name": record[1],
        #         "data_folder": record[2],
        #         "archive_folder": record[3],
        #         "delete_folder": record[4],
        #         "archive_days": record[5],
        #         "delete_days": record[6],
        #         "is_Active": record[7],
        #         "email_receipt": record[8],
        #         "create_by": record[9],
        #         "created_on": record[10]
                
        #     })
        
        #connection.commit()
        # Print the array
        print("Records stored in array:")
        print("Total Records ", records)
        print("Total Records ", len(records))
        
        #return records_array 
        return records
    
    except mysql.connector.Error as err:
        print(f"Error while select records from table archival_batch_items: {err}")
    finally:
        cursor.close()
    
if __name__ == "__main__":
    config = load_config()
    connection = connect_to_mariadb(config)
    #create_table_if_not_exists(connection)
    records = get_all_archival_batch_items(connection)
