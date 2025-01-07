import traceback
from prettytable import PrettyTable
import logging

class ErrorLogger:



    def __init__(self):
        # Dictionary to store errors: { "source": "error code" }
        self.errors = {}
        self.logger = logging.getLogger(__name__)
        table = PrettyTable()
        self.table.field_names = ["Source", "Error Code"]

    def log_error(self, src, error_code):
        self.errors[src] = error_code

    def print_errors(self):
        
        status=0

        if not self.errors:
            self.logger.info("No errors logged.")
            return
        
        for src, error_code in self.errors.items():
            self.table.add_row([src, error_code])
            status=1
        
        self.logger.info(self.table)
        return status 


    def get_table(self):
        """Return the PrettyTable object."""
        return self.table
    
# Example Usage
if __name__ == "__main__":
    elogger = ErrorLogger()
    #logger = logging.getLogger(__name__)
    
    # Simulating errors
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        elogger.log_error("Division Operation", str(e))
        elogger.log_error("Traceback", traceback.format_exc())

    try:
        with open("nonexistent_file.txt", "r") as f:
            content = f.read()
    except FileNotFoundError as e:
        elogger.log_error("File Read Operation", str(e))
        elogger.log_error("Traceback", traceback.format_exc())

    # Print errors
    elogger.print_errors()
