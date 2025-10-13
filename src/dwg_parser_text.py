"""
DWG/DXF File Parser
Parses AutoCAD DWG/DXF files and extracts relevant information
"""

import ezdxf
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import math

@dataclass
class LayerInfo:
    """Represents a layer in the drawing"""
    name: str
    color: int
    is_visible: bool
    line_type: str = "CONTINUOUS"

@dataclass
class EntityInfo:
    """Represents an entity in the drawing"""
    entity_type: str
    layer: str
    handle: str
    data: Dict[str, Any]

@dataclass
class DrawingInfo:
    """Represents drawing information"""
    filename: str
    version: str
    units: str
    layers: List[LayerInfo]
    entities: List[EntityInfo]
    dimensions: List[Dict[str, Any]]
    text_entities: List[Dict[str, Any]]
    blocks: List[Dict[str, Any]]

class DWGParser:
    """Parser for DWG/DXF files"""
    
    def __init__(self):
        self.drawing_info = None
        self.measurements = []
    
    def parse_file(self, file_path: str) -> Optional[DrawingInfo]:
        """Parse a DWG/DXF file"""
        try:
            # Load the DXF document
            doc = ezdxf.readfile(file_path)
            msp = doc.modelspace()
            
            # Extract basic information
            filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
            version = doc.dxfversion
            units = self._get_units(doc)
            
            # Extract layers
            layers = self._extract_layers(doc)
            
            # Extract entities
            entities = self._extract_entities(msp)
            
            # Extract dimensions
            dimensions = self._extract_dimensions(msp)
            
            # Extract text entities
            text_entities = self._extract_text_entities(msp)
            
            # Extract blocks
            blocks = self._extract_blocks(doc)
            
            # Create drawing info object
            self.drawing_info = DrawingInfo(
                filename=filename,
                version=version,
                units=units,
                layers=layers,
                entities=entities,
                dimensions=dimensions,
                text_entities=text_entities,
                blocks=blocks
            )
            
            # Extract measurements
            self.measurements = self._extract_measurements()
            
            return self.drawing_info
            
        except Exception as e:
            print(f"Error parsing DWG file: {e}")
            return None
    
    def _get_units(self, doc) -> str:
        """Get drawing units"""
        try:
            units = doc.header.get('$INSUNITS', 0)
            unit_map = {
                0: 'unitless',
                1: 'inches',
                2: 'feet',
                4: 'millimeters',
                5: 'centimeters',
                6: 'meters'
            }
            return unit_map.get(units, 'unknown')
        except:
            return 'unknown'
    
    def _extract_layers(self, doc) -> List[LayerInfo]:
        """Extract layer information"""
        layers = []
        try:
            for layer in doc.layers:
                layer_info = LayerInfo(
                    name=layer.dxf.name,
                    color=layer.dxf.color,
                    is_visible=not layer.is_off(),
                    line_type=layer.dxf.linetype
                )
                layers.append(layer_info)
        except Exception as e:
            print(f"Error extracting layers: {e}")
        return layers
    
    def _extract_entities(self, msp) -> List[EntityInfo]:
        """Extract entity information"""
        entities = []
        try:
            for entity in msp:
                entity_info = EntityInfo(
                    entity_type=entity.dxftype(),
                    layer=entity.dxf.layer,
                    handle=entity.dxf.handle,
                    data=self._extract_entity_data(entity)
                )
                entities.append(entity_info)
        except Exception as e:
            print(f"Error extracting entities: {e}")
        return entities
    
    def _extract_entity_data(self, entity) -> Dict[str, Any]:
        """Extract specific data from an entity"""
        data = {}
        try:
            if entity.dxftype() == 'LINE':
                data = {
                    'start': (entity.dxf.start.x, entity.dxf.start.y, entity.dxf.start.z),
                    'end': (entity.dxf.end.x, entity.dxf.end.y, entity.dxf.end.z),
                    'length': self._calculate_line_length(entity)
                }
            elif entity.dxftype() == 'CIRCLE':
                data = {
                    'center': (entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z),
                    'radius': entity.dxf.radius,
                    'area': math.pi * entity.dxf.radius ** 2
                }
            elif entity.dxftype() == 'ARC':
                data = {
                    'center': (entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z),
                    'radius': entity.dxf.radius,
                    'start_angle': entity.dxf.start_angle,
                    'end_angle': entity.dxf.end_angle
                }
            elif entity.dxftype() == 'TEXT':
                data = {
                    'text': entity.dxf.text,
                    'height': entity.dxf.height,
                    'position': (entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z)
                }
            elif entity.dxftype() == 'DIMENSION':
                data = {
                    'text': entity.dxf.text,
                    'measurement': self._extract_dimension_value(entity)
                }
        except Exception as e:
            print(f"Error extracting entity data: {e}")
        return data
    
    def _calculate_line_length(self, line_entity) -> float:
        """Calculate line length"""
        try:
            start = line_entity.dxf.start
            end = line_entity.dxf.end
            return math.sqrt((end.x - start.x)**2 + (end.y - start.y)**2 + (end.z - start.z)**2)
        except:
            return 0.0
    
    def _extract_dimensions(self, msp) -> List[Dict[str, Any]]:
        """Extract dimension information"""
        dimensions = []
        try:
            for entity in msp.query('DIMENSION'):
                dim_data = {
                    'text': entity.dxf.text,
                    'layer': entity.dxf.layer,
                    'measurement': self._extract_dimension_value(entity)
                }
                dimensions.append(dim_data)
        except Exception as e:
            print(f"Error extracting dimensions: {e}")
        return dimensions
    
    def _extract_dimension_value(self, dim_entity) -> float:
        """Extract numeric value from dimension"""
        try:
            text = dim_entity.dxf.text
            # Try to extract numeric value from dimension text
            import re
            numbers = re.findall(r'[\d.]+', text)
            if numbers:
                return float(numbers[0])
        except:
            pass
        return 0.0
    
    def _extract_text_entities(self, msp) -> List[Dict[str, Any]]:
        """Extract text entity information"""
        text_entities = []
        try:
            for entity in msp.query('TEXT'):
                text_data = {
                    'text': entity.dxf.text,
                    'height': entity.dxf.height,
                    'layer': entity.dxf.layer,
                    'position': (entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z)
                }
                text_entities.append(text_data)
        except Exception as e:
            print(f"Error extracting text entities: {e}")
        return text_entities
    
    def _extract_blocks(self, doc) -> List[Dict[str, Any]]:
        """Extract block information"""
        blocks = []
        try:
            for block in doc.blocks:
                if not block.is_any_layout:
                    block_data = {
                        'name': block.name,
                        'entity_count': len(block)
                    }
                    blocks.append(block_data)
        except Exception as e:
            print(f"Error extracting blocks: {e}")
        return blocks
    
    def _extract_measurements(self) -> List[Dict[str, Any]]:
        """Extract measurements from the drawing"""
        measurements = []
        
        if not self.drawing_info:
            return measurements
        
        try:
            # Extract measurements from dimensions
            for dim in self.drawing_info.dimensions:
                if dim['measurement'] > 0:
                    measurements.append({
                        'type': 'dimension',
                        'value': dim['measurement'],
                        'layer': dim['layer'],
                        'text': dim['text']
                    })
            
            # Extract measurements from line lengths
            for entity in self.drawing_info.entities:
                if entity.entity_type == 'LINE' and 'length' in entity.data:
                    measurements.append({
                        'type': 'line_length',
                        'value': entity.data['length'],
                        'layer': entity.layer
                    })
                elif entity.entity_type == 'CIRCLE' and 'radius' in entity.data:
                    measurements.append({
                        'type': 'radius',
                        'value': entity.data['radius'],
                        'layer': entity.layer
                    })
            
            # Extract measurements from text entities
            for text in self.drawing_info.text_entities:
                import re
                numbers = re.findall(r'[\d.]+', text['text'])
                for number in numbers:
                    try:
                        value = float(number)
                        if value > 0:
                            measurements.append({
                                'type': 'text_measurement',
                                'value': value,
                                'layer': text['layer'],
                                'text': text['text']
                            })
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error extracting measurements: {e}")
        
        return measurements
    
    def get_measurements(self) -> List[Dict[str, Any]]:
        """Get all measurements from the drawing"""
        return self.measurements
    
    def export_to_json(self, output_path: str):
        """Export drawing information to JSON"""
        if not self.drawing_info:
            print("No drawing data to export")
            return
        
        import json
        
        data = {
            'filename': self.drawing_info.filename,
            'version': self.drawing_info.version,
            'units': self.drawing_info.units,
            'layers': [
                {
                    'name': layer.name,
                    'color': layer.color,
                    'is_visible': layer.is_visible,
                    'line_type': layer.line_type
                }
                for layer in self.drawing_info.layers
            ],
            'entities': [
                {
                    'entity_type': entity.entity_type,
                    'layer': entity.layer,
                    'handle': entity.handle,
                    'data': entity.data
                }
                for entity in self.drawing_info.entities
            ],
            'dimensions': self.drawing_info.dimensions,
            'text_entities': self.drawing_info.text_entities,
            'blocks': self.drawing_info.blocks,
            'measurements': self.measurements
        }
        
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    
    def print_summary(self):
        """Print a summary of the drawing"""
        if not self.drawing_info:
            print("No drawing data available")
            return
        
        print(f"DWG Parser Summary")
        print(f"File: {self.drawing_info.filename}")
        print(f"Version: {self.drawing_info.version}")
        print(f"Units: {self.drawing_info.units}")
        print(f"Layers: {len(self.drawing_info.layers)}")
        print(f"Entities: {len(self.drawing_info.entities)}")
        print(f"Dimensions: {len(self.drawing_info.dimensions)}")
        print(f"Text entities: {len(self.drawing_info.text_entities)}")
        print(f"Blocks: {len(self.drawing_info.blocks)}")
        print(f"Measurements: {len(self.measurements)}")

if __name__ == "__main__":
    import sys
    parser = DWGParser()
    if len(sys.argv) < 2:
        print("Usage: python src/dwg_parser_text.py <input_file.dxf>")
    else:
        input_file = sys.argv[1]
        output_file = "dwg_output.json"
        drawing_info = parser.parse_file(input_file)
        if drawing_info:
            parser.export_to_json(output_file)
            print(f"DWG parsed and exported to {output_file}")
        else:
            print("Parsing failed.")
