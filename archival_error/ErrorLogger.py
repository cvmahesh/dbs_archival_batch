import traceback
from prettytable import PrettyTable

class ErrorLogger:
    def __init__(self):
        # Dictionary to store errors: { "source": "error code" }
        self.errors = {}

    def log_error(self, src, error_code):
        self.errors[src] = error_code

    def print_errors(self):
        
        status=0

        if not self.errors:
            print("No errors logged.")
            return
        
        table = PrettyTable()
        table.field_names = ["Source", "Error Code"]
        for src, error_code in self.errors.items():
            table.add_row([src, error_code])
            status=1
        
        print(table)
        return status 
        
# Example Usage
if __name__ == "__main__":
    logger = ErrorLogger()

    # Simulating errors
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.log_error("Division Operation", str(e))
        logger.log_error("Traceback", traceback.format_exc())

    try:
        with open("nonexistent_file.txt", "r") as f:
            content = f.read()
    except FileNotFoundError as e:
        logger.log_error("File Read Operation", str(e))
        logger.log_error("Traceback", traceback.format_exc())

    # Print errors
    logger.print_errors()
