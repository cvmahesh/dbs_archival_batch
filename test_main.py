import unittest
from unittest.mock import patch
import main  # Assuming `main.py` is in the same directory

class TestMainArguments(unittest.TestCase):
    @patch("sys.argv", ["main.py", "--archive"])
    def test_archive(self):
        result = main.main()
        self.assertEqual(result, "Files archived successfully.")

    # @patch("sys.argv", ["main.py", "--listfiles"])
    # def test_list_files(self):
    #     result = main.main()
    #     self.assertEqual(result, "Files listed successfully.")

    @patch("sys.argv", ["main.py", "--rollback"])
    def test_rollback(self):
        result = main.main()
        self.assertEqual(result, "Rollback completed successfully.")

    @patch("sys.argv", ["main.py"])
    def test_no_action(self):
        result = main.main()
        self.assertEqual(result, "No action performed.")

if __name__ == "__main__":
    unittest.main()