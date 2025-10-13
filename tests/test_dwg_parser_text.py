import unittest
from unittest.mock import patch, MagicMock
import sys

# Import the module under test
import src.dwg_parser_text as dwg_parser_text

class TestDWGParserText(unittest.TestCase):
    def setUp(self):
        # If there is a main class, instantiate it here
        if hasattr(dwg_parser_text, 'DWGParser'):
            self.parser = dwg_parser_text.DWGParser()
        else:
            self.parser = None

    def test_module_import(self):
        self.assertTrue(hasattr(dwg_parser_text, '__file__'))

    def test_methods_exist(self):
        # Check for expected methods (update as needed)
        expected_methods = [
            'parse_file', 'parse_content', 'extract_layers', 'extract_entities',
            'get_entities_by_layer', 'get_entities_by_type', 'export_to_json', 'print_summary'
        ]
        for method in expected_methods:
            self.assertTrue(hasattr(dwg_parser_text, method) or (self.parser and hasattr(self.parser, method)))

    def test_parse_file(self):
        if hasattr(dwg_parser_text, 'parse_file'):
            with patch('builtins.open', unittest.mock.mock_open(read_data='data')) as mock_file:
                result = dwg_parser_text.parse_file('fakefile.dwg')
                self.assertIsNotNone(result)
        elif self.parser and hasattr(self.parser, 'parse_file'):
            with patch('builtins.open', unittest.mock.mock_open(read_data='data')) as mock_file:
                result = self.parser.parse_file('fakefile.dwg')
                self.assertIsNotNone(result)

    # Add more tests for other methods as needed, using mocks for file I/O

if __name__ == '__main__':
    unittest.main()
