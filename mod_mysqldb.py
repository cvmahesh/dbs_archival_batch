import mysql.connector
from mysql.connector import Error
import yaml


# Load YAML configuration file
def load_config():
    with open('file_config.yaml', 'r') as file:
        return yaml.safe_load(file)
    

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

if __name__ == "__main__":
    config = load_config()
    connection = connect_to_mariadb(config)
    #create_table_if_not_exists(connection)
    #records = get_all_archival_batch_items(connection)
