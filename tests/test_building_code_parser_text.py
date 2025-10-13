import unittest
from unittest.mock import patch, mock_open
from src.building_code_parser_text import OntarioBuildingCodeParserfromtext, BuildingCodeStructure, Section
import textwrap

class TestOntarioBuildingCodeParserfromtext(unittest.TestCase):
    def setUp(self):
        self.parser = OntarioBuildingCodeParserfromtext()
        self.sample_content = """
Division A
Part 1
Title of Part 1
Section 1.1
Title of Section 1.1
1.1.1
Title of Article 1.1.1
1.1.1.1
Title of Subarticle 1.1.1.1
1) Clause one.
2) Clause two.
Division B
Part 2
Title of Part 2
Section 2.1
Title of Section 2.1
2.1.1
Title of Article 2.1.1
2.1.1.1
Title of Subarticle 2.1.1.1
1) Clause one.
"""

    def test_parse_content(self):
        structure = self.parser.parse_content(self.sample_content)
        self.assertIsInstance(structure, BuildingCodeStructure)
        self.assertEqual(len(structure.divisions), 2)

    def test_parse_content_structure(self):
        content = textwrap.dedent('''
        Division A
        Part 1
        Title of Part 1
        Section 1.1
        Title of Section 1.1
        1.1.1
        Title of Article 1.1.1
        1.1.1.1
        Title of Subarticle 1.1.1.1
        1) Clause one.
        ''')
        structure = self.parser.parse_content(content)
        self.assertEqual(len(structure.divisions), 1)
        self.assertEqual(structure.divisions[0].letter, 'A')
        self.assertEqual(structure.divisions[0].parts[0].number, '1')

    @patch("builtins.open", new_callable=mock_open, read_data="Division A\nPart 1\nTitle\nSection 1.1\nTitle\n1.1.1\nTitle\n1.1.1.1\nTitle\n1) Clause\n")
    def test_parse_file(self, mock_file):
        structure = self.parser.parse_file("fakefile.txt")
        self.assertIsInstance(structure, BuildingCodeStructure)

    def test_get_measurements_by_unit(self):
        self.parser.structure = BuildingCodeStructure(divisions=[], measurements=[{'unit': 'meters', 'value': 2, 'context': '', 'full_match': '2 meters'}], requirements=[])
        result = self.parser.get_measurements_by_unit('meters')
        self.assertEqual(len(result), 1)

    def test_get_requirements_by_keyword(self):
        self.parser.structure = BuildingCodeStructure(divisions=[], measurements=[], requirements=["shall be concrete.", "must be steel."])
        result = self.parser.get_requirements_by_keyword('concrete')
        self.assertEqual(result, ["shall be concrete."])

    def test_find_section_by_number(self):
        section = Section(number="1.1", title="Test", content="", articles=[])
        self.parser.structure = BuildingCodeStructure(
            divisions=[
                type('Division', (), {'parts': [type('Part', (), {'sections': [section]})()]})()
            ],
            measurements=[],
            requirements=[]
        )
        found = self.parser.find_section_by_number("1.1")
        self.assertEqual(found, section)

    @patch("builtins.open", new_callable=mock_open)
    def test_export_to_json(self, mock_file):
        self.parser.structure = BuildingCodeStructure(divisions=[], measurements=[], requirements=[])
        self.parser.export_to_json("output.json")
        mock_file.assert_called_with("output.json", 'w', encoding='utf-8')

    def test_print_summary_no_structure(self):
        self.parser.structure = None
        with patch("builtins.print") as mock_print:
            self.parser.print_summary()
            mock_print.assert_any_call("No structure parsed")

if __name__ == "__main__":
    unittest.main()
