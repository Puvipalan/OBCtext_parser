import unittest
from unittest.mock import patch, MagicMock
import sys

# Import the module under test
import src.dwg_validator_text as dwg_validator_text
from src.dwg_validator_text import DWGValidator, ValidationResult
from src.dwg_parser_text import DrawingInfo, LayerInfo, EntityInfo

class MockDWGParser:
    def parse_file(self, file_path):
        # Return a minimal DrawingInfo for testing
        return DrawingInfo(
            filename="test.dxf",
            version="AC1027",
            units="meters",
            layers=[LayerInfo(name="A-WALL", color=7, is_visible=True)],
            entities=[EntityInfo(entity_type="LINE", layer="A-WALL", handle="1", data={"length": 5.0})],
            dimensions=[{"text": "5.0", "layer": "A-WALL", "measurement": 5.0}],
            text_entities=[{"text": "5.0m", "height": 0.2, "layer": "A-WALL", "position": (0,0,0)}],
            blocks=[]
        )

class TestDWGValidatorText(unittest.TestCase):
    def setUp(self):
        # If there is a main class, instantiate it here
        if hasattr(dwg_validator_text, 'DWGValidator'):
            self.validator = dwg_validator_text.DWGValidator()
        else:
            self.validator = None

    def test_module_import(self):
        self.assertTrue(hasattr(dwg_validator_text, '__file__'))

    def test_methods_exist(self):
        # Check for expected methods (update as needed)
        expected_methods = [
            'validate_file', 'validate_content', 'check_layers', 'check_entities',
            'get_errors', 'export_to_json', 'print_summary'
        ]
        for method in expected_methods:
            self.assertTrue(hasattr(dwg_validator_text, method) or (self.validator and hasattr(self.validator, method)))

    def test_validate_file(self):
        if hasattr(dwg_validator_text, 'validate_file'):
            with patch('builtins.open', unittest.mock.mock_open(read_data='data')) as mock_file:
                result = dwg_validator_text.validate_file('fakefile.dwg')
                self.assertIsNotNone(result)
        elif self.validator and hasattr(self.validator, 'validate_file'):
            with patch('builtins.open', unittest.mock.mock_open(read_data='data')) as mock_file:
                result = self.validator.validate_file('fakefile.dwg')
                self.assertIsNotNone(result)

    def test_validate_file_pass(self):
        validator = DWGValidator(dwg_parser_text=MockDWGParser())
        results = validator.validate_file(dwg_file_path="dummy.dxf")
        self.assertTrue(any(r.status == "PASS" for r in results))

    def test_validate_file_fail_on_missing_info(self):
        class EmptyParser:
            def parse_file(self, file_path): return None
        validator = DWGValidator(dwg_parser_text=EmptyParser())
        results = validator.validate_file(dwg_file_path="dummy.dxf")
        self.assertEqual(results[0].status, "FAIL")
        self.assertIn("Could not parse", results[0].message)

    # Add more tests for other methods as needed, using mocks for file I/O

if __name__ == '__main__':
    unittest.main()
