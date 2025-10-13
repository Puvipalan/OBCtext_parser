"""
DWG File Validator
Performs various checks on DWG files against building codes and standards
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import logging
import json
import os

from dwg_parser_text import DWGParser, DrawingInfo, LayerInfo, EntityInfo
from building_code_parser_text import OntarioBuildingCodeParserfromtext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DWGValidator")

@dataclass
class ValidationResult:
    """Represents a validation result"""
    check_name: str
    status: str  # 'PASS', 'FAIL', 'WARNING'
    message: str
    details: Dict[str, Any]

class DWGValidator:
    """
    Validator for DWG files against building codes.
    Accepts custom parsers for testability.
    """
    def __init__(
        self,
        dwg_parser: Optional[DWGParser] = None,
        building_code_parser: Optional[OntarioBuildingCodeParserfromtext] = None,
        tolerance: float = 0.1
    ):
        self.dwg_parser = dwg_parser or DWGParser()
        self.building_code_parser = building_code_parser
        self.tolerance = tolerance
        self.validation_results: List[ValidationResult] = []
        self.unit_conversion = {
            'inches': 1.0,
            'feet': 12.0,
            'millimeters': 0.0393701,
            'centimeters': 0.393701,
            'meters': 39.3701
        }

    def validate_file(
        self,
        dwg_file_path: Optional[str] = None,
        drawing_info: Optional[DrawingInfo] = None
    ) -> List[ValidationResult]:
        """
        Validate a DWG file or DrawingInfo object against building codes.
        """
        self.validation_results = []

        if drawing_info is None:
            if not dwg_file_path:
                self.validation_results.append(ValidationResult(
                    check_name="File Parsing",
                    status="FAIL",
                    message="No file path or DrawingInfo provided",
                    details={}
                ))
                return self.validation_results
            drawing_info = self.dwg_parser.parse_file(dwg_file_path)

        if not drawing_info:
            self.validation_results.append(ValidationResult(
                check_name="File Parsing",
                status="FAIL",
                message="Could not parse DWG file",
                details={}
            ))
            return self.validation_results

        try:
            self._check_drawing_units(drawing_info)
            self._check_layer_standards(drawing_info)
            self._check_dimension_completeness(drawing_info)
            self._check_text_readability(drawing_info)
            self._check_scale_consistency(drawing_info)
            self._check_entity_organization(drawing_info)
            if self.building_code_parser:
                self._check_against_building_codes(drawing_info)
        except Exception as e:
            logger.exception("Validation failed with exception")
            self.validation_results.append(ValidationResult(
                check_name="Validation Exception",
                status="FAIL",
                message=f"Exception during validation: {e}",
                details={"exception": str(e)}
            ))

        return self.validation_results

    def _check_drawing_units(self, drawing_info: DrawingInfo):
        units = drawing_info.units.lower()
        if units in ['feet', 'inches', 'meters', 'millimeters']:
            status = "PASS"
            message = f"Drawing units ({units}) are appropriate for building drawings"
        else:
            status = "WARNING"
            message = f"Drawing units ({units}) may not be standard for building drawings"
        self.validation_results.append(ValidationResult(
            check_name="Drawing Units",
            status=status,
            message=message,
            details={'units': units}
        ))

    def _check_layer_standards(self, drawing_info: DrawingInfo):
        layer_names = [layer.name for layer in drawing_info.layers]
        standard_prefixes = ['A-', 'S-', 'E-', 'P-', 'F-', 'C-', 'D-', 'T-']
        has_standard_layers = any(
            any(layer.startswith(prefix) for prefix in standard_prefixes)
            for layer in layer_names
        )
        layer_count = len(layer_names)
        if has_standard_layers and layer_count > 5:
            status = "PASS"
            message = "Layer organization follows common standards"
        elif layer_count > 5:
            status = "WARNING"
            message = "Layers present but may not follow standard naming conventions"
        else:
            status = "WARNING"
            message = "Limited layer organization detected"
        self.validation_results.append(ValidationResult(
            check_name="Layer Standards",
            status=status,
            message=message,
            details={
                'layer_count': layer_count,
                'has_standard_layers': has_standard_layers,
                'layer_names': layer_names[:10]
            }
        ))

    def _check_dimension_completeness(self, drawing_info: DrawingInfo):
        dimensions = drawing_info.dimensions
        text_entities = drawing_info.text_entities
        dim_count = len(dimensions)
        text_count = len(text_entities)
        measurement_texts = []
        for text in text_entities:
            text_content = text['text'].lower()
            if any(char.isdigit() for char in text_content) and any(unit in text_content for unit in ['ft', 'in', 'm', 'mm', '"', "'"]):
                measurement_texts.append(text['text'])
        total_measurements = dim_count + len(measurement_texts)
        if total_measurements >= 10:
            status = "PASS"
            message = f"Drawing has adequate dimensions ({total_measurements} total)"
        elif total_measurements >= 5:
            status = "WARNING"
            message = f"Drawing has some dimensions but may need more ({total_measurements} total)"
        else:
            status = "FAIL"
            message = f"Drawing appears to lack sufficient dimensions ({total_measurements} total)"
        self.validation_results.append(ValidationResult(
            check_name="Dimension Completeness",
            status=status,
            message=message,
            details={
                'dimension_count': dim_count,
                'text_count': text_count,
                'measurement_texts': measurement_texts[:5],
                'total_measurements': total_measurements
            }
        ))

    def _check_text_readability(self, drawing_info: DrawingInfo):
        text_entities = drawing_info.text_entities
        if not text_entities:
            self.validation_results.append(ValidationResult(
                check_name="Text Readability",
                status="WARNING",
                message="No text entities found in drawing",
                details={}
            ))
            return
        heights = [text['height'] for text in text_entities if text.get('height', 0) > 0]
        if not heights:
            status = "WARNING"
            message = "Text height information not available"
        else:
            min_height = min(heights)
            max_height = max(heights)
            avg_height = sum(heights) / len(heights)
            if min_height >= 0.1:
                status = "PASS"
                message = f"Text appears to be readable (min height: {min_height:.3f})"
            else:
                status = "WARNING"
                message = f"Some text may be too small (min height: {min_height:.3f})"
        self.validation_results.append(ValidationResult(
            check_name="Text Readability",
            status=status,
            message=message,
            details={
                'text_count': len(text_entities),
                'heights': heights[:10],
                'min_height': min(heights) if heights else 0,
                'max_height': max(heights) if heights else 0,
                'avg_height': sum(heights) / len(heights) if heights else 0
            }
        ))

    def _check_scale_consistency(self, drawing_info: DrawingInfo):
        measurements = self.dwg_parser.get_measurements()
        if len(measurements) < 2:
            self.validation_results.append(ValidationResult(
                check_name="Scale Consistency",
                status="WARNING",
                message="Insufficient measurements to check scale consistency",
                details={'measurement_count': len(measurements)}
            ))
            return
        values = [
            m['value'] for m in measurements
            if isinstance(m['value'], (int, float)) and m['value'] > 0
        ]
        if len(values) < 2:
            status = "WARNING"
            message = "Insufficient numeric measurements for scale check"
            ratio = 0
        else:
            values.sort()
            ratio = values[-1] / values[0] if values[0] > 0 else float('inf')
            if ratio < 1000:
                status = "PASS"
                message = f"Scale appears consistent (ratio: {ratio:.1f})"
            else:
                status = "WARNING"
                message = f"Scale may be inconsistent (ratio: {ratio:.1f})"
        self.validation_results.append(ValidationResult(
            check_name="Scale Consistency",
            status=status,
            message=message,
            details={
                'measurement_count': len(measurements),
                'value_count': len(values),
                'min_value': min(values) if values else 0,
                'max_value': max(values) if values else 0,
                'ratio': ratio
            }
        ))

    def _check_entity_organization(self, drawing_info: DrawingInfo):
        entities = drawing_info.entities
        entity_types = {}
        for entity in entities:
            entity_type = getattr(entity, 'entity_type', None)
            if entity_type:
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        total_entities = len(entities)
        unique_types = len(entity_types)
        if total_entities == 0:
            status = "WARNING"
            message = "No entities found in drawing"
        elif unique_types >= 3:
            status = "PASS"
            message = f"Good entity organization ({unique_types} types, {total_entities} total)"
        elif unique_types >= 2:
            status = "WARNING"
            message = f"Limited entity variety ({unique_types} types, {total_entities} total)"
        else:
            status = "WARNING"
            message = f"Very limited entity types ({unique_types} types, {total_entities} total)"
        self.validation_results.append(ValidationResult(
            check_name="Entity Organization",
            status=status,
            message=message,
            details={
                'total_entities': total_entities,
                'unique_types': unique_types,
                'entity_types': entity_types
            }
        ))

    def _check_against_building_codes(self, drawing_info: DrawingInfo):
        if not self.building_code_parser or not getattr(self.building_code_parser, "structure", None):
            self.validation_results.append(ValidationResult(
                check_name="Building Code Compliance",
                status="WARNING",
                message="No building code structure available for comparison",
                details={}
            ))
            return
        code_measurements = self.building_code_parser.structure.measurements
        drawing_measurements = self.dwg_parser.get_measurements()
        if not code_measurements:
            self.validation_results.append(ValidationResult(
                check_name="Building Code Compliance",
                status="WARNING",
                message="No building code measurements available for comparison",
                details={}
            ))
            return
        code_values = []
        for measurement in code_measurements:
            value = measurement['value']
            unit = measurement['unit']
            inches = value * self.unit_conversion.get(unit, 1.0)
            code_values.append(inches)
        drawing_values = [
            m['value'] for m in drawing_measurements
            if isinstance(m['value'], (int, float))
        ]
        if not drawing_values:
            self.validation_results.append(ValidationResult(
                check_name="Building Code Compliance",
                status="WARNING",
                message="No measurable values found in drawing",
                details={}
            ))
            return
        code_min = min(code_values) if code_values else 0
        code_max = max(code_values) if code_values else 0
        drawing_min = min(drawing_values)
        drawing_max = max(drawing_values)
        # Tolerance-based check
        if code_min > 0 and drawing_min > 0:
            ratio_min = drawing_min / code_min
            ratio_max = drawing_max / code_max if code_max > 0 else 1
            if (1 - self.tolerance) <= ratio_min <= (1 + self.tolerance) and (1 - self.tolerance) <= ratio_max <= (1 + self.tolerance):
                status = "PASS"
                message = "Drawing measurements appear consistent with building codes"
            else:
                status = "WARNING"
                message = "Drawing measurements may not align with building code requirements"
        else:
            status = "WARNING"
            message = "Unable to compare measurements with building codes"
        self.validation_results.append(ValidationResult(
            check_name="Building Code Compliance",
            status=status,
            message=message,
            details={
                'code_measurements': len(code_values),
                'drawing_measurements': len(drawing_values),
                'code_range': (code_min, code_max),
                'drawing_range': (drawing_min, drawing_max)
            }
        ))

    def get_summary(self) -> Dict[str, Any]:
        if not self.validation_results:
            return {'status': 'No validation performed', 'results': []}
        pass_count = sum(1 for result in self.validation_results if result.status == 'PASS')
        warning_count = sum(1 for result in self.validation_results if result.status == 'WARNING')
        fail_count = sum(1 for result in self.validation_results if result.status == 'FAIL')
        overall_status = 'PASS'
        if fail_count > 0:
            overall_status = 'FAIL'
        elif warning_count > 0:
            overall_status = 'WARNING'
        return {
            'overall_status': overall_status,
            'total_checks': len(self.validation_results),
            'pass_count': pass_count,
            'warning_count': warning_count,
            'fail_count': fail_count,
            'results': [
                {
                    'check_name': result.check_name,
                    'status': result.status,
                    'message': result.message,
                    'details': result.details
                }
                for result in self.validation_results
            ]
        }

    def print_summary(self):
        summary = self.get_summary()
        print(f"DWG Validation Summary")
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Total Checks: {summary['total_checks']}")
        print(f"Passed: {summary['pass_count']}")
        print(f"Warnings: {summary['warning_count']}")
        print(f"Failed: {summary['fail_count']}")
        print()
        for result in summary['results']:
            status_symbol = {'PASS': '✓', 'WARNING': '⚠', 'FAIL': '✗'}.get(result['status'], '?')
            print(f"{status_symbol} {result['check_name']}: {result['message']}")

    def export_results(self, output_dir: str = ".", filename: str = None):
        """
        Export validation results to a JSON file in the specified directory.
        If filename is not provided, use 'validation_results.json'.
        """
        if not self.validation_results:
            raise ValueError("No validation results to export. Run validate_file() first.")
        os.makedirs(output_dir, exist_ok=True)
        if not filename:
            filename = "validation_results.json"
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([result.__dict__ for result in self.validation_results], f, indent=2)
        logger.info(f"Validation results exported to {output_path}")

def drawing_info_from_json(json_data: dict) -> DrawingInfo:
    layers = [LayerInfo(**layer) for layer in json_data['layers']]
    entities = [EntityInfo(**entity) for entity in json_data['entities']]
    return DrawingInfo(
        filename=json_data['filename'],
        version=json_data['version'],
        units=json_data['units'],
        layers=layers,
        entities=entities,
        dimensions=json_data['dimensions'],
        text_entities=json_data['text_entities'],
        blocks=json_data['blocks']
    )

if __name__ == "__main__":
    # Example usage
    import sys
    code_parser = OntarioBuildingCodeParserfromtext()
    validator = DWGValidator(building_code_parser=code_parser)
    print("DWG Validator ready. Use validate_file() method with a DXF file path.")      
    # results = validator.validate_file(dwg_file_path="your_file.dxf")
    # or, if you have DrawingInfo from JSON:
    # results = validator.validate_file(drawing_info=your_drawing_info)
    with open('dwg_output.json', 'r', encoding='utf-8') as f:   
        json_data = json.load(f)
    drawing_info = drawing_info_from_json(json_data)
    validator.validate_file(drawing_info=drawing_info)
    summary = validator.get_summary()
    print(summary)
    # Export results to project folder
    validator.export_results(output_dir=".", filename="validation_results.json")
