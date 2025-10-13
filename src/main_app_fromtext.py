"""
Main Application with GUI
Provides a graphical interface for building code parsing and DWG validation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
from typing import Optional
import threading

from building_code_parser_text import OntarioBuildingCodeParserfromtext
from dwg_parser_text import DWGParser
from dwg_validator_text import DWGValidator

class BuildingCodeDWGApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Building Code & DWG Analysis Tool")
        self.root.geometry("1200x800")
        
        # Initialize parsers
        self.building_code_parser = OntarioBuildingCodeParserfromtext()
        self.dwg_parser = DWGParser()
        self.validator = DWGValidator()
        
        # File paths
        self.building_code_file = None
        self.dwg_file = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Building Code & DWG Analysis Tool", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # Building code file selection
        ttk.Label(file_frame, text="Building Code File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.building_code_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.building_code_var, state="readonly").grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_building_code_file).grid(row=0, column=2, pady=2)
        
        # DWG file selection
        ttk.Label(file_frame, text="DWG/DXF File:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.dwg_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.dwg_file_var, state="readonly").grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=2)
        ttk.Button(file_frame, text="Browse", 
                  command=self.browse_dwg_file).grid(row=1, column=2, pady=2)
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)
        
        # Parse buttons
        ttk.Button(control_frame, text="Parse Building Code", 
                  command=self.parse_building_code).grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(control_frame, text="Parse DWG File", 
                  command=self.parse_dwg_file).grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(control_frame, text="Validate DWG", 
                  command=self.validate_dwg).grid(row=0, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Analysis buttons
        ttk.Button(control_frame, text="Compare with Codes", 
                  command=self.compare_with_codes).grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(control_frame, text="Export Results", 
                  command=self.export_results).grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(control_frame, text="Clear All", 
                  command=self.clear_all).grid(row=1, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Results notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Building code results tab
        self.building_code_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.building_code_frame, text="Building Code Results")
        
        self.building_code_text = scrolledtext.ScrolledText(self.building_code_frame, wrap=tk.WORD)
        self.building_code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # DWG results tab
        self.dwg_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dwg_frame, text="DWG Results")
        
        self.dwg_text = scrolledtext.ScrolledText(self.dwg_frame, wrap=tk.WORD)
        self.dwg_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Validation results tab
        self.validation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.validation_frame, text="Validation Results")
        
        self.validation_text = scrolledtext.ScrolledText(self.validation_frame, wrap=tk.WORD)
        self.validation_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def browse_building_code_file(self):
        """Browse for building code file"""
        file_path = filedialog.askopenfilename(
            title="Select Building Code File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.building_code_file = file_path
            self.building_code_var.set(os.path.basename(file_path))
            self.status_var.set(f"Building code file selected: {os.path.basename(file_path)}")
    
    def browse_dwg_file(self):
        """Browse for DWG/DXF file"""
        file_path = filedialog.askopenfilename(
            title="Select DWG/DXF File",
            filetypes=[("DXF files", "*.dxf"), ("DWG files", "*.dwg"), ("All files", "*.*")]
        )
        if file_path:
            self.dwg_file = file_path
            self.dwg_file_var.set(os.path.basename(file_path))
            self.status_var.set(f"DWG file selected: {os.path.basename(file_path)}")
    
    def parse_building_code(self):
        """Parse building code file"""
        if not self.building_code_file:
            messagebox.showerror("Error", "Please select a building code file first.")
            return
        
        self.status_var.set("Parsing building code...")
        self.root.update()
        
        try:
            structure = self.building_code_parser.parse_file(self.building_code_file)
            
            # Display results
            self.building_code_text.delete(1.0, tk.END)
            self.building_code_text.insert(tk.END, "Building Code Parse Results\n")
            self.building_code_text.insert(tk.END, "=" * 50 + "\n\n")
            
            if structure and structure.divisions:
                self.building_code_text.insert(tk.END, f"Total divisions found: {len(structure.divisions)}\n")
                
                total_parts = sum(len(div.parts) for div in structure.divisions if div.parts)
                total_sections = sum(len(part.sections) for div in structure.divisions if div.parts for part in div.parts if part.sections)
                
                self.building_code_text.insert(tk.END, f"Total parts: {total_parts}\n")
                self.building_code_text.insert(tk.END, f"Total sections: {total_sections}\n")
                self.building_code_text.insert(tk.END, f"Total measurements: {len(structure.measurements)}\n")
                self.building_code_text.insert(tk.END, f"Total requirements: {len(structure.requirements)}\n\n")
                
                # Display divisions and their content
                for division in structure.divisions:
                    self.building_code_text.insert(tk.END, f"Division {division.letter}\n")
                    self.building_code_text.insert(tk.END, "-" * 30 + "\n")
                    
                    if division.parts:
                        for part in division.parts[:3]:  # Show first 3 parts
                            self.building_code_text.insert(tk.END, f"  Part {part.number}: {part.title}\n")
                            
                            if part.sections:
                                for section in part.sections[:2]:  # Show first 2 sections per part
                                    self.building_code_text.insert(tk.END, f"    Section {section.number}: {section.title}\n")
                    
                    self.building_code_text.insert(tk.END, "\n")
                
                # Display measurements
                if structure.measurements:
                    self.building_code_text.insert(tk.END, "Measurements found:\n")
                    for measurement in structure.measurements[:10]:  # Show first 10 measurements
                        self.building_code_text.insert(tk.END, 
                            f"  • {measurement['value']} {measurement['unit']} - {measurement['context'][:50]}...\n")
                
                # Display requirements
                if structure.requirements:
                    self.building_code_text.insert(tk.END, "\nRequirements found:\n")
                    for req in structure.requirements[:5]:  # Show first 5 requirements
                        self.building_code_text.insert(tk.END, f"  • {req[:100]}...\n")
            else:
                self.building_code_text.insert(tk.END, "No structure found in the building code file.\n")
            
            # Switch to building code tab
            self.notebook.select(0)
            self.status_var.set("Building code parsed successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing building code: {str(e)}")
            self.status_var.set("Error parsing building code")
    
    def parse_dwg_file(self):
        """Parse DWG file"""
        if not self.dwg_file:
            messagebox.showerror("Error", "Please select a DWG/DXF file first.")
            return
        
        self.status_var.set("Parsing DWG file...")
        self.root.update()
        
        try:
            drawing_info = self.dwg_parser.parse_file(self.dwg_file)
            
            # Display results
            self.dwg_text.delete(1.0, tk.END)
            self.dwg_text.insert(tk.END, "DWG Parse Results\n")
            self.dwg_text.insert(tk.END, "=" * 50 + "\n\n")
            
            if drawing_info:
                self.dwg_text.insert(tk.END, f"File: {drawing_info.filename}\n")
                self.dwg_text.insert(tk.END, f"Version: {drawing_info.version}\n")
                self.dwg_text.insert(tk.END, f"Units: {drawing_info.units}\n")
                self.dwg_text.insert(tk.END, f"Layers: {len(drawing_info.layers)}\n")
                self.dwg_text.insert(tk.END, f"Entities: {len(drawing_info.entities)}\n")
                self.dwg_text.insert(tk.END, f"Dimensions: {len(drawing_info.dimensions)}\n")
                self.dwg_text.insert(tk.END, f"Text entities: {len(drawing_info.text_entities)}\n")
                self.dwg_text.insert(tk.END, f"Blocks: {len(drawing_info.blocks)}\n\n")
                
                # Entity type breakdown
                entity_types = {}
                for entity in drawing_info.entities:
                    entity_type = entity.entity_type
                    entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
                
                self.dwg_text.insert(tk.END, "Entity Types:\n")
                for entity_type, count in sorted(entity_types.items()):
                    self.dwg_text.insert(tk.END, f"  {entity_type}: {count}\n")
                
                # Layer information
                self.dwg_text.insert(tk.END, "\nLayers:\n")
                for layer in drawing_info.layers[:10]:  # Show first 10 layers
                    self.dwg_text.insert(tk.END, f"  {layer.name} (color: {layer.color}, visible: {layer.is_visible})\n")
                
                # Measurements
                measurements = self.dwg_parser.get_measurements()
                if measurements:
                    self.dwg_text.insert(tk.END, f"\nMeasurements ({len(measurements)} total):\n")
                    for measurement in measurements[:10]:  # Show first 10 measurements
                        self.dwg_text.insert(tk.END, f"  {measurement['type']}: {measurement['value']} (layer: {measurement['layer']})\n")
            else:
                self.dwg_text.insert(tk.END, "Could not parse DWG file.\n")
            
            # Switch to DWG tab
            self.notebook.select(1)
            self.status_var.set("DWG file parsed successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing DWG file: {str(e)}")
            self.status_var.set("Error parsing DWG file")
    
    def validate_dwg(self):
        """Validate DWG file"""
        if not self.dwg_file:
            messagebox.showerror("Error", "Please select a DWG/DXF file first.")
            return
        
        self.status_var.set("Validating DWG file...")
        self.root.update()
        
        try:
            # Set building code parser if available
            if self.building_code_parser.structure:
                self.validator.building_code_parser = self.building_code_parser
            
            validation_results = self.validator.validate_file(self.dwg_file)
            
            # Display results
            self.validation_text.delete(1.0, tk.END)
            self.validation_text.insert(tk.END, "DWG Validation Results\n")
            self.validation_text.insert(tk.END, "=" * 50 + "\n\n")
            
            if validation_results:
                summary = self.validator.get_summary()
                self.validation_text.insert(tk.END, f"Overall Status: {summary['overall_status']}\n")
                self.validation_text.insert(tk.END, f"Total Checks: {summary['total_checks']}\n")
                self.validation_text.insert(tk.END, f"Passed: {summary['pass_count']}\n")
                self.validation_text.insert(tk.END, f"Warnings: {summary['warning_count']}\n")
                self.validation_text.insert(tk.END, f"Failed: {summary['fail_count']}\n\n")
                
                for result in validation_results:
                    status_symbol = {'PASS': '✓', 'WARNING': '⚠', 'FAIL': '✗'}[result.status]
                    self.validation_text.insert(tk.END, f"{status_symbol} {result.check_name}\n")
                    self.validation_text.insert(tk.END, f"   {result.message}\n")
                    if result.details:
                        self.validation_text.insert(tk.END, f"   Details: {json.dumps(result.details, indent=2)}\n")
                    self.validation_text.insert(tk.END, "\n")
            else:
                self.validation_text.insert(tk.END, "No validation results available.\n")
            
            # Switch to validation tab
            self.notebook.select(2)
            self.status_var.set("DWG validation completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error validating DWG file: {str(e)}")
            self.status_var.set("Error validating DWG file")
    
    def compare_with_codes(self):
        """Compare DWG measurements with building codes"""
        if not self.building_code_parser.structure:
            messagebox.showwarning("Warning", "Please parse building code file first.")
            return
        
        if not self.dwg_parser.drawing_info:
            messagebox.showwarning("Warning", "Please parse DWG file first.")
            return
        
        self.status_var.set("Comparing with building codes...")
        self.root.update()
        
        try:
            # Get measurements from both sources
            code_measurements = self.building_code_parser.structure.measurements
            dwg_measurements = self.dwg_parser.get_measurements()
            
            # Display comparison
            self.validation_text.delete(1.0, tk.END)
            self.validation_text.insert(tk.END, "Building Code vs DWG Comparison\n")
            self.validation_text.insert(tk.END, "=" * 50 + "\n\n")
            
            self.validation_text.insert(tk.END, f"Building Code Measurements: {len(code_measurements)}\n")
            self.validation_text.insert(tk.END, f"DWG Measurements: {len(dwg_measurements)}\n\n")
            
            if code_measurements:
                self.validation_text.insert(tk.END, "Building Code Measurements:\n")
                for measurement in code_measurements[:10]:  # Show first 10
                    self.validation_text.insert(tk.END, 
                        f"  • {measurement['value']} {measurement['unit']} - {measurement['context'][:50]}...\n")
            
            if dwg_measurements:
                self.validation_text.insert(tk.END, "\nDWG Measurements:\n")
                for measurement in dwg_measurements[:10]:  # Show first 10
                    self.validation_text.insert(tk.END, 
                        f"  • {measurement['value']} ({measurement['type']}) - Layer: {measurement['layer']}\n")
            
            # Switch to validation tab
            self.notebook.select(2)
            self.status_var.set("Comparison completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error comparing with codes: {str(e)}")
            self.status_var.set("Error in comparison")
    
    def export_results(self):
        """Export results to files"""
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        if not export_dir:
            return
        
        try:
            # Export building code results
            if self.building_code_parser.structure:
                self.building_code_parser.export_to_json(os.path.join(export_dir, "building_code_results.json"))
            
            # Export DWG results
            if self.dwg_parser.drawing_info:
                self.dwg_parser.export_to_json(os.path.join(export_dir, "dwg_results.json"))
            
            # Export validation results
            if self.validator.validation_results:
                summary = self.validator.get_summary()
                with open(os.path.join(export_dir, "validation_results.json"), 'w') as f:
                    json.dump(summary, f, indent=2)
            
            messagebox.showinfo("Success", f"Results exported to {export_dir}")
            self.status_var.set("Results exported successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting results: {str(e)}")
            self.status_var.set("Error exporting results")
    
    def clear_all(self):
        """Clear all data and results"""
        self.building_code_file = None
        self.dwg_file = None
        self.building_code_var.set("")
        self.dwg_file_var.set("")
        
        self.building_code_parser = OntarioBuildingCodeParser()
        self.dwg_parser = DWGParser()
        self.validator = DWGValidator()
        
        self.building_code_text.delete(1.0, tk.END)
        self.dwg_text.delete(1.0, tk.END)
        self.validation_text.delete(1.0, tk.END)
        
        self.status_var.set("All data cleared")
        self.notebook.select(0)

def main():
    """Main function"""
    root = tk.Tk()
    app = BuildingCodeDWGApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
