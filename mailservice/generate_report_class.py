from jinja2 import Template

# from flask import Flask, render_template
from prettytable import PrettyTable
from datetime import datetime

class DirectoryReportGenerator:
    def __init__(self, ignore_items, processed_dir_items):
        """
        Initialize the report generator with ignore and processed directory lists.
        """
        
        self.ignore_items = ignore_items
        # self.table_html=table_html
        self.processed_dir_items = processed_dir_items
        

    
    def generate_error_table(self):
        logger = PrettyTable()
        logger.field_names = ["Timestamp", "Error Code", "Error Message"]
        
        # Log some sample errors
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.add_row([timestamp, 404, "Page not found"])
        logger.add_row([timestamp, 500, "Internal server error"])
        logger.add_row([timestamp, 403, "Forbidden access"])

        # Return the table as an HTML string
        print(f"logger :: {logger}")
        #return logger.get_html_string()
        return logger.get_html_string(attributes={"class": "pretty-table"})



    def generate_html(self):
        self.table_html = self.generate_error_table()
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Directory Processing Report</title>
            <style>
                body {
                    background-color: black;
                    color: white;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin: 0;
                    padding: 0;
                    width: 100%;
                }
                h1 {
                    color: white;
                    background-color: red;
                    font-size: 32px;
                    padding: 10px;
                    margin: 20px auto;
                    border-radius: 8px;
                    width: 90%;
                }
                h2 {
                    color: white;
                    background-color: red;
                    font-size: 24px;
                    padding: 10px;
                    margin-top: 30px;
                    margin-left: 20%;
                    margin-right: 20%;
                    border-radius: 5px;
                }
                ul {
                    list-style-type: none;
                    padding: 0;
                    margin: 0;
                }
                li {
                    padding: 10px;
                    margin: 10px;
                    background-color: white;
                    color: black;
                    font-size: 18px;
                    border-radius: 5px;
                    width: 300px;
                    margin-left: auto;
                    margin-right: auto;
                }
                li:hover {
                    background-color: lightgray;
                    color: black;
                }
                table {
                    width: 100%;
                    border-spacing: 0;
                    padding: 0;
 
                }
                td {
                    padding: 0 10px;
                }
                th {
                    #background-color: #f2f2f2;
                    width: 100%;
                }
                 
                .center-container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    #height: 100vh; /* Full viewport height */
                    width: 100%;
                    margin: 0;
                    #background-color: #f9f9f9;
                    font-family: Arial, sans-serif;
                }

                table.pretty-table {
                    margin-left: auto;
                    margin-right: auto;
                    width: 60%; /* Matches the <h2> width */
                    border-collapse: collapse;
                }

                table.pretty-table th,
                table.pretty-table td {
                    border: 1px solid white;
                    padding: 10px;
                    text-align: center;
                }

                table.pretty-table th {
                    background-color: red;
                    color: white;
                }

                table.pretty-table td {
                    background-color: black;
                    color: white;
                }
                
            </style>
        </head>
        <body>
            <table border=1 align="center" width="100%" cellspacing="0" cellpadding="10" style="background-color: black;">
                <tr>
                     
                    <td align="center" style="padding: 20px;">
                        <h1>Archival Batch Processing Report</h1>
                        <h2>Ignored Items</h2>
                        <ul>
                            {% for item in ignore_items %}
                                <li>{{ item }}</li>
                            {% endfor %}
                        </ul>
                        <h2>Processed Directories</h2>
                        <ul>
                            {% for dir in processed_dir_items %}
                                <li>{{ dir }}</li>
                            {% endfor %}
                        </ul>
                        <h2>Pretty Report</h2>
                        <div>
                            {{ table_html|safe }}
                        </div>
                    </td>
                     
                    
                </tr>
               
               
            </table>
        </body>
        </html>
        """
        template = Template(html_template)
        return template.render(ignore_items=self.ignore_items, processed_dir_items=self.processed_dir_items, table_html=self.table_html)

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
    # Sample data
    ignore_items = ["temp", "log", "cache"]
    processed_dir_items = ["dir1", "dir2", "dir3"]
    # Create an instance of the report generator
    report_generator = DirectoryReportGenerator(ignore_items, processed_dir_items)
    #report_generator.generate_error_table()
    # Generate and save the report
    report_generator.save_to_file("report.html")



#python3 mailservice/generate_report_class.py