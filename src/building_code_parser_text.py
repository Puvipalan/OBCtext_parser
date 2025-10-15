"""
Ontario Building Code Text Parser
Parses Ontario Building Code text files and extracts relevant information
Handles Division, Part, Section, Article, Subarticle, and Clauses structure
"""

import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Clause:
    """Represents a clause within a subarticle"""
    number: str  # e.g., "1)", "2)", "a)", "b)", "i)", "ii)"
    content: str
    sub_clauses: list['Clause'] = field(default_factory=list)

@dataclass
class Subarticle:
    """Represents a subarticle within an article"""
    number: str  # e.g., "9.1.1.1"
    title: str
    content: str
    clauses: list[Clause] = field(default_factory=list)

@dataclass
class Article:
    """Represents an article within a section"""
    number: str  # e.g., "9.1.1"
    title: str
    content: str
    subarticles: list[Subarticle] = field(default_factory=list)

@dataclass
class Section:
    """Represents a section within a part"""
    number: str  # e.g., "9.1"
    title: str
    content: str
    articles: list[Article] = field(default_factory=list)

@dataclass
class Part:
    """Represents a part within a division"""
    number: str  # e.g., "9"
    title: str
    content: str
    sections: list[Section] = field(default_factory=list)

@dataclass
class Division:
    """Represents a division of the building code"""
    letter: str  # e.g., "A", "B", "C"
    content: str
    parts: list[Part] = field(default_factory=list)

@dataclass
class BuildingCodeStructure:
    """Complete building code structure"""
    divisions: List[Division]
    measurements: List[Dict[str, Any]]
    requirements: List[str]

class OntarioBuildingCodeParserfromtext:
    """Parser for Ontario Building Code text files"""
    
    def __init__(self):
        self.structure = None
        self.measurement_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:feet|ft|meters?|m|inches?|in|mm|cm|kPa|MPa|kN|kg)\b',
            r'minimum\s+(\d+(?:\.\d+)?)\s*(?:feet|ft|meters?|m|inches?|in|mm|cm|kPa|MPa|kN|kg)\b',
            r'maximum\s+(\d+(?:\.\d+)?)\s*(?:feet|ft|meters?|m|inches?|in|mm|cm|kPa|MPa|kN|kg)\b',
            r'not\s+less\s+than\s+(\d+(?:\.\d+)?)\s*(?:feet|ft|meters?|m|inches?|in|mm|cm|kPa|MPa|kN|kg)\b',
            r'not\s+more\s+than\s+(\d+(?:\.\d+)?)\s*(?:feet|ft|meters?|m|inches?|in|mm|cm|kPa|MPa|kN|kg)\b',
            r'(\d+(?:\.\d+)?)\s*(?:kPa|MPa|kN|kg)\b',
            r'(\d+(?:\.\d+)?)\s*(?:mm|cm)\b'
        ]
    
    def parse_file(self, file_path: str) -> BuildingCodeStructure:
        """Parse a building code text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            return self.parse_content(content)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    def parse_content(self, content: str) -> BuildingCodeStructure:
        """Parse building code content with Ontario Building Code structure"""
        divisions = []
        all_measurements = []
        all_requirements = []
        
        # Split content by divisions
        division_pattern = r'^Division\s+([A-Z])\s*\n(.*?)(?=^Division\s+[A-Z]|\Z)'
        division_matches = re.finditer(division_pattern, content, re.MULTILINE | re.DOTALL)
        
        for div_match in division_matches:
            div_letter = div_match.group(1)
            div_content = div_match.group(2).strip()
            
            # Parse parts within division
            parts = self._parse_parts(div_content)
            
            division = Division(
                letter=div_letter,
                content=div_content,
                parts=parts
            )
            divisions.append(division)
            
            # Extract measurements and requirements from this division
            div_measurements = self._extract_measurements(div_content)
            div_requirements = self._extract_requirements(div_content)
            
            all_measurements.extend(div_measurements)
            all_requirements.extend(div_requirements)
        
        self.structure = BuildingCodeStructure(
            divisions=divisions,
            measurements=all_measurements,
            requirements=all_requirements
        )
        
        return self.structure
    
    def _parse_parts(self, content: str) -> List[Part]:
        """Parse parts within division content"""
        parts = []
        
        # Pattern to match "Part X" followed by title and content
        part_pattern = r'^Part\s+(\d+)\s*\n([^\n]+)\s*\n(.*?)(?=^Part\s+\d+|\Z)'
        part_matches = re.finditer(part_pattern, content, re.MULTILINE | re.DOTALL)
        
        for part_match in part_matches:
            part_num = part_match.group(1)
            part_title = part_match.group(2).strip()
            part_content = part_match.group(3).strip()
            
            # Parse sections within part
            sections = self._parse_sections(part_content)
            
            part = Part(
                number=part_num,
                title=part_title,
                content=part_content,
                sections=sections
            )
            parts.append(part)
        
        return parts
    
    def _parse_sections(self, content: str) -> List[Section]:
        """Parse sections within part content"""
        sections = []
        
        # Pattern to match "Section X.Y" followed by title and content
        section_pattern = r'^Section\s+(\d+\.\d+)\s*\.?\s*\n([^\n]+)\s*\n(.*?)(?=^Section\s+\d+\.\d+|\Z)'
        section_matches = re.finditer(section_pattern, content, re.MULTILINE | re.DOTALL)
        
        for section_match in section_matches:
            section_num = section_match.group(1)
            section_title = section_match.group(2).strip()
            section_content = section_match.group(3).strip()
            
            # Parse articles within section
            articles = self._parse_articles(section_content)
            
            section = Section(
                number=section_num,
                title=section_title,
                content=section_content,
                articles=articles
            )
            sections.append(section)
        
        return sections
    
    def _parse_articles(self, content: str) -> List[Article]:
        """Parse articles within section content"""
        articles = []
        
        # Pattern to match "X.Y.Z" followed by title and content
        article_pattern = r'^(\d+\.\d+\.\d+)\s*\.?\s*\n([^\n]+)\s*\n(.*?)(?=^\d+\.\d+\.\d+|\Z)'
        article_matches = re.finditer(article_pattern, content, re.MULTILINE | re.DOTALL)
        
        for article_match in article_matches:
            article_num = article_match.group(1)
            article_title = article_match.group(2).strip()
            article_content = article_match.group(3).strip()
            
            # Parse subarticles within article
            subarticles = self._parse_subarticles(article_content)
            
            article = Article(
                number=article_num,
                title=article_title,
                content=article_content,
                subarticles=subarticles
            )
            articles.append(article)
        
        return articles
    
    def _parse_subarticles(self, content: str) -> List[Subarticle]:
        """Parse subarticles within article content"""
        subarticles = []
        
        # Pattern to match "X.Y.Z.W" followed by title and content
        subarticle_pattern = r'^(\d+\.\d+\.\d+\.\d+)\s*\.?\s*\n([^\n]+)\s*\n(.*?)(?=^\d+\.\d+\.\d+\.\d+|\Z)'
        subarticle_matches = re.finditer(subarticle_pattern, content, re.MULTILINE | re.DOTALL)
        
        for subarticle_match in subarticle_matches:
            subarticle_num = subarticle_match.group(1)
            subarticle_title = subarticle_match.group(2).strip()
            subarticle_content = subarticle_match.group(3).strip()
            
            # Parse clauses within subarticle
            clauses = self._parse_clauses(subarticle_content)
            
            subarticle = Subarticle(
                number=subarticle_num,
                title=subarticle_title,
                content=subarticle_content,
                clauses=clauses
            )
            subarticles.append(subarticle)
        
        return subarticles
    
    def _parse_clauses(self, content: str) -> List[Clause]:
        """Parse clauses within subarticle content"""
        clauses = []
        
        # Pattern to match numbered clauses like "1)", "2)", "a)", "b)", "i)", "ii)"
        clause_pattern = r'^(\d+\)|[a-z]\)|[ivx]+\))\s+(.*?)(?=^\d+\)|^[a-z]\)|^[ivx]+\)|\Z)'
        clause_matches = re.finditer(clause_pattern, content, re.MULTILINE | re.DOTALL)
        
        for clause_match in clause_matches:
            clause_num = clause_match.group(1)
            clause_content = clause_match.group(2).strip()
            
            # Parse sub-clauses within clause
            sub_clauses = self._parse_sub_clauses(clause_content)
            
            clause = Clause(
                number=clause_num,
                content=clause_content,
                sub_clauses=sub_clauses
            )
            clauses.append(clause)
        
        return clauses
    
    def _parse_sub_clauses(self, content: str) -> List[Clause]:
        """Parse sub-clauses within clause content"""
        sub_clauses = []
        
        # Pattern to match sub-clauses like "a)", "b)", "i)", "ii)"
        sub_clause_pattern = r'^([a-z]\)|[ivx]+\))\s+(.*?)(?=^[a-z]\)|^[ivx]+\)|\Z)'
        sub_clause_matches = re.finditer(sub_clause_pattern, content, re.MULTILINE | re.DOTALL)
        
        for sub_clause_match in sub_clause_matches:
            sub_clause_num = sub_clause_match.group(1)
            sub_clause_content = sub_clause_match.group(2).strip()
            
            sub_clause = Clause(
                number=sub_clause_num,
                content=sub_clause_content
            )
            sub_clauses.append(sub_clause)
        
        return sub_clauses
    
    def _extract_requirements(self, content: str) -> List[str]:
        """Extract requirement statements from content"""
        requirements = []
        
        # Look for requirement patterns
        req_patterns = [
            r'shall\s+[^.]*\.',
            r'must\s+[^.]*\.',
            r'required\s+[^.]*\.',
            r'mandatory\s+[^.]*\.',
            r'conform\s+[^.]*\.',
            r'comply\s+[^.]*\.'
        ]
        
        for pattern in req_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                requirements.append(match.group().strip())
        
        return requirements
    
    def _extract_measurements(self, content: str) -> List[Dict[str, Any]]:
        """Extract measurements from content"""
        measurements = []
        
        for pattern in self.measurement_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                value = float(match.group(1))
                unit = self._extract_unit(match.group(0))
                context = self._get_context(content, match.start(), match.end())
                
                measurements.append({
                    'value': value,
                    'unit': unit,
                    'context': context,
                    'full_match': match.group(0)
                })
        
        return measurements
    
    def _extract_unit(self, text: str) -> str:
        """Extract unit from measurement text"""
        text_lower = text.lower()
        if 'feet' in text_lower or 'ft' in text_lower:
            return 'feet'
        elif 'meter' in text_lower or 'm\b' in text_lower:
            return 'meters'
        elif 'inch' in text_lower or 'in\b' in text_lower:
            return 'inches'
        elif 'mm' in text_lower:
            return 'millimeters'
        elif 'cm' in text_lower:
            return 'centimeters'
        elif 'kpa' in text_lower:
            return 'kilopascals'
        elif 'mpa' in text_lower:
            return 'megapascals'
        elif 'kn' in text_lower:
            return 'kilonewtons'
        elif 'kg' in text_lower:
            return 'kilograms'
        return 'unknown'
    
    def _get_context(self, content: str, start: int, end: int, context_length: int = 100) -> str:
        """Get context around a match"""
        context_start = max(0, start - context_length)
        context_end = min(len(content), end + context_length)
        return content[context_start:context_end].strip()
    
    def get_measurements_by_unit(self, unit: str) -> List[Dict[str, Any]]:
        """Get all measurements of a specific unit"""
        if not self.structure:
            return []
        return [m for m in self.structure.measurements if m['unit'] == unit]
    
    def get_requirements_by_keyword(self, keyword: str) -> List[str]:
        """Get all requirements containing a specific keyword"""
        if not self.structure:
            return []
        return [req for req in self.structure.requirements if keyword.lower() in req.lower()]
    
    def find_section_by_number(self, section_number: str) -> Optional[Section]:
        """Find a section by its number"""
        if not self.structure:
            return None
        
        for division in self.structure.divisions:
            if division.parts:
                for part in division.parts:
                    if part.sections:
                        for section in part.sections:
                            if section.number == section_number:
                                return section
        return None
    
    def export_to_json(self, output_path: str):
        """Export parsed data to JSON"""
        if not self.structure:
            print("No structure to export")
            return
        
        def serialize_obj(obj):
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if isinstance(value, list):
                        result[key] = [serialize_obj(item) for item in value]
                    elif hasattr(value, '__dict__'):
                        result[key] = serialize_obj(value)
                    else:
                        result[key] = value
                return result
            return obj
        
        data = {
            'structure': serialize_obj(self.structure),
            'summary': {
                'total_divisions': len(self.structure.divisions),
                'total_parts': sum(len(div.parts) for div in self.structure.divisions if div.parts),
                'total_sections': sum(len(part.sections) for div in self.structure.divisions if div.parts for part in div.parts if part.sections),
                'total_measurements': len(self.structure.measurements),
                'total_requirements': len(self.structure.requirements)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    
    def print_summary(self):
        """Print a summary of parsed data"""
        if not self.structure:
            print("No structure parsed")
            return
        
        print("Ontario Building Code Parser Summary")
        print("=" * 50)
        
        print(f"Total divisions: {len(self.structure.divisions)}")
        
        total_parts = 0
        total_sections = 0
        total_articles = 0
        total_subarticles = 0
        total_clauses = 0
        
        for division in self.structure.divisions:
            if division.parts:
                total_parts += len(division.parts)
                for part in division.parts:
                    if part.sections:
                        total_sections += len(part.sections)
                        for section in part.sections:
                            if section.articles:
                                total_articles += len(section.articles)
                                for article in section.articles:
                                    if article.subarticles:
                                        total_subarticles += len(article.subarticles)
                                        for subarticle in article.subarticles:
                                            if subarticle.clauses:
                                                total_clauses += len(subarticle.clauses)
        
        print(f"Total parts: {total_parts}")
        print(f"Total sections: {total_sections}")
        print(f"Total articles: {total_articles}")
        print(f"Total subarticles: {total_subarticles}")
        print(f"Total clauses: {total_clauses}")
        print(f"Total requirements: {len(self.structure.requirements)}")
        print(f"Total measurements: {len(self.structure.measurements)}")
        
        # Group measurements by unit
        unit_counts = {}
        for measurement in self.structure.measurements:
            unit = measurement['unit']
            unit_counts[unit] = unit_counts.get(unit, 0) + 1
        
        print("\nMeasurements by unit:")
        for unit, count in sorted(unit_counts.items()):
            print(f"  {unit}: {count}")

if __name__ == "__main__":
    # Example usage
    parser = OntarioBuildingCodeParserfromtext()
    
    # Parse the example building code file
    structure = parser.parse_file("section_building_code.txt")
    
    if structure:
        parser.print_summary()
        
        # Export to JSON
        parser.export_to_json("section_building_code_parsed_fromtext.json")
        
        # Example queries
        print("\nExample queries:")
        print("Measurements in meters:")
        meter_measurements = parser.get_measurements_by_unit("meters")
        for measurement in meter_measurements[:5]:  # Show first 5
            print(f"  {measurement['value']} {measurement['unit']} - {measurement['context'][:50]}...")
        
        print("\nRequirements containing 'concrete':")
        concrete_requirements = parser.get_requirements_by_keyword("concrete")
        for req in concrete_requirements[:3]:  # Show first 3
            print(f"  {req[:100]}...")