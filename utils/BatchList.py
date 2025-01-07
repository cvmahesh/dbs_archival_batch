class EntryList:
    def __init__(self):
        self.entries = []

    def add_entry(self, serial_number, description, remarks):
        entry = {
            "serial_number": serial_number,
            "description": description,
            "remarks": remarks,
        }
        self.entries.append(entry)

    def print_entries(self):
        for entry in self.entries:
            print(f"Serial Number: {entry['serial_number']}, Description: {entry['description']}, Remarks: {entry['remarks']}")

# Create an instance of the EntryList class
entry_list = EntryList()

# Add entries using the method
entry_list.add_entry(1, "Item A", "Delivered")
entry_list.add_entry(2, "Item B", "Pending")
entry_list.add_entry(3, "Item C", "In Progress")

# Print the entries
entry_list.print_entries()
