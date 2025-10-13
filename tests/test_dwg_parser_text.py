import unittest
from unittest.mock import patch, MagicMock
from src.dwg_parser_text import DWGParser

class TestDWGParser(unittest.TestCase):
    def setUp(self):
        self.parser = DWGParser()

    @patch('src.dwg_parser_text.ezdxf.readfile')
    def test_parse_file_returns_drawing_info(self, mock_readfile):
        # Setup mock DXF document and modelspace
        mock_doc = MagicMock()
        mock_doc.modelspace.return_value = MagicMock()
        mock_doc.dxfversion = 'AC1027'
        mock_doc.header.get.return_value = 6  # meters
        mock_doc.layers = []
        mock_doc.blocks = []
        mock_readfile.return_value = mock_doc

        result = self.parser.parse_file('fakefile.dxf')
        self.assertIsNotNone(result)
        self.assertEqual(result.version, 'AC1027')
        self.assertEqual(result.units, 'meters')
