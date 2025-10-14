# Ontario Building Code & DWG Analysis Tool

This project provides tools to parse and analyze Ontario Building Code text files and validate DWG/DXF drawings for compliance. It includes a GUI for interactive use and supports extraction of measurements, requirements, and drawing information.

---

## Features

- **Parse Ontario Building Code**: Extracts structure, measurements, and requirements from text files.
- **DWG/DXF Parsing**: Extracts layers, entities, dimensions, and measurements from CAD files.
- **Validation**: Checks DWG files for compliance with building code requirements.
- **GUI Application**: User-friendly interface for file selection, parsing, validation, and exporting results.

---

## Installation

### 1. Clone the Repository
git clone https://github.com/Puvipalan/OBCtext_parser.git cd OBCtext_parser

### 2. Install Python Dependencies

It is recommended to use a virtual environment:
python -m venv venv

On Windows:
venv\Scripts\activate
On macOS/Linux:
source venv/bin/activate


Install all required packages:
pip install -r requirements.txt

### 3. Install Tesseract OCR

- **Windows**:  
  Download the installer from [UB Mannheim builds](https://github.com/tesseract-ocr/tesseract/wiki#windows) and add the install directory to your `PATH`.
- **macOS**:  

brew install tesseract
- **Linux**:  
sudo apt-get install tesseract-ocr

### 4. Install Poppler

- **Windows**:  
  Download from [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/) and add the `bin` directory to your `PATH`.
- **macOS**:  

brew install poppler

- **Linux**: 
sudo apt-get install poppler-utils

---

## Usage

### GUI Application

Run the main application:
python -m src.main_app_fromtext

- Use the GUI to select a building code text file and a DWG/DXF file.
- Parse, validate, and export results using the provided buttons.

### Command-Line Usage

#### Parse a Building Code File
python src/building_code_parser_text.py path/to/building_code.txt

#### Parse a DWG/DXF File
python src/dwg_parser.py path/to/dwg_or_dxf_file

#### Validate a Drawing
python src/dwg_validator.py path/to/dwg_file

python src/dwg_validator_text.py

---

## Notes

- For table extraction from PDFs, ensure that Tesseract and Poppler are installed and available in your system `PATH`.
- Some features require additional system dependencies (see `requirements.txt` comments).
- For best results, use clean, OCR-friendly PDF/text files and standard-compliant DWG/DXF files.

---

## Testing

Run unit tests with:


## License

[MIT License](LICENSE)

