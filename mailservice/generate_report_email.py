from pathlib import Path
from jinja2 import Template
from prettytable import PrettyTable
from datetime import datetime

class DirectoryReportGenerator:
    def __init__(self, ignore_items, processed_dir_items):
        """
        Initialize the report generator with ignore and processed directory lists.
        """
        self.ignore_items = ignore_items
        self.processed_dir_items = processed_dir_items
        # Set the path to the template file in the config directory
        self.template_path = Path(__file__).resolve().parent.parent / "config" / "report_template.html"

    def generate_error_table(self):
        logger = PrettyTable()
        logger.field_names = ["Timestamp", "Error Code", "Error Message"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.add_row([timestamp, 404, "Page not found"])
        logger.add_row([timestamp, 500, "Internal server error"])
        logger.add_row([timestamp, 403, "Forbidden access"])
        return logger.get_html_string(attributes={"class": "pretty-table"})

    def generate_html(self):
        self.table_html = self.generate_error_table()
        # Read the template file
        with open(self.template_path, "r") as file:
            html_template = file.read()
        template = Template(html_template)
        return template.render(
            ignore_items=self.ignore_items,
            processed_dir_items=self.processed_dir_items,
            table_html=self.table_html
        )

    def save_to_file(self, filename):
        """
        Save the generated HTML content to a file.
        """
        html_content = self.generate_html()
        with open(filename, "w") as file:
            file.write(html_content)
        print(f"HTML report generated: {filename}")

# Example usage
if __name__ == "__main__":
    ignore_items = ["temp", "log", "cache"]
    processed_dir_items = ["dir1", "dir2", "dir3"]
    report_generator = DirectoryReportGenerator(ignore_items, processed_dir_items)
    report_generator.save_to_file("report.html")
