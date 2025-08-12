"""Main extraction orchestrator"""

import os
import datetime
from pathlib import Path
from typing import Dict, Any

from core.file_analyzer import FileAnalyzer
from core.header_extractor import HeaderExtractor  
from core.opencascade_processor import OpenCASCADEProcessor
from core.web_converter import WebConverter
from model.extraction_data import OpenCASCADEData
from output.output_manager import OutputManager

class MainExtractor:
    """Main extraction orchestrator that coordinates all modules"""
    
    def __init__(self):
        # Initialize all processing modules
        self.file_analyzer = FileAnalyzer()
        self.header_extractor = HeaderExtractor()
        self.opencascade_processor = OpenCASCADEProcessor()
        self.web_converter = WebConverter()
        self.output_manager = OutputManager()
        
        # Track processing statistics
        self.extraction_stats = {
            "processed_entities": 0,
            "errors": [],
            "data_types_found": set()
        }
    
    def extract_all_stp_data(self, input_path: str, output_dir: str) -> Dict[str, Any]:
        """Main extraction method that coordinates all modules"""
        
        print(f"🔄 Dynamic extraction from: {os.path.basename(input_path)}")
        print(f"Debug: OpenCASCADE available = {self.opencascade_processor.opencascade_available}")
        
        # Initialize comprehensive data structure
        stp_data = {
            "extraction_info": self._get_extraction_metadata(input_path),
            "file_analysis": {},
            "step_header": {},
            "entities": {},
            "assembly_structure": {},
            "part_data": {},
            "materials": {},
            "colors": {},
            "geometry_analysis": {},
            "topology_details": {},
            "relationships": {},
            "custom_attributes": {},
            "web_assets": {},
            "extraction_statistics": {}
        }
        
        try:
            # Step 1: Analyze file structure
            print("  📋 Analyzing file structure...")
            file_analysis = self.file_analyzer.analyze_file_structure(input_path)
            stp_data["file_analysis"] = file_analysis.__dict__
            
            # Step 2: Extract STEP header
            print("  📄 Extracting STEP header...")
            header_data = self.header_extractor.extract_step_header(input_path)
            stp_data["step_header"] = header_data.__dict__
            
            # Step 3: Process with OpenCASCADE if available
            if self.opencascade_processor.opencascade_available:
                print("  🔧 Processing with OpenCASCADE...")
                try:
                    occ_data = self.opencascade_processor.extract_with_opencascade(input_path)
                    self._merge_opencascade_data(stp_data, occ_data)
                    print("  ✅ OpenCASCADE processing completed!")
                except Exception as e:
                    print(f"  ❌ OpenCASCADE processing failed: {str(e)}")
                    self.extraction_stats["errors"].append(f"OpenCASCADE: {str(e)}")
            else:
                print("  ⚠️ OpenCASCADE not available - skipping detailed extraction")
            
            # Step 4: Convert to web format
            if self.web_converter.cascadio_available:
                print("  🌐 Converting to web format...")
                web_assets = self.web_converter.convert_to_web_format(input_path, output_dir)
                stp_data["web_assets"] = web_assets.__dict__
            else:
                print("  ⚠️ Cascadio not available - skipping web conversion")
            
            # Step 5: Generate extraction statistics
            stp_data["extraction_statistics"] = self._generate_extraction_stats()
            
            # Step 6: Save all extracted data
            self.output_manager.save_dynamic_output(stp_data, output_dir)
            
            print("  ✅ Dynamic extraction complete!")
            return stp_data
            
        except Exception as e:
            print(f"  ❌ Extraction error: {str(e)}")
            stp_data["extraction_info"]["extraction_error"] = str(e)
            self.extraction_stats["errors"].append(str(e))
            return stp_data
    
    def _get_extraction_metadata(self, input_path: str) -> Dict[str, Any]:
        """Get metadata about the extraction process"""
        file_stat = os.stat(input_path)
        
        return {
            "source_file": {
                "filename": os.path.basename(input_path),
                "full_path": str(Path(input_path).absolute()),
                "file_size_bytes": file_stat.st_size,
                "file_size_mb": round(file_stat.st_size / 1024 / 1024, 2),
                "last_modified": datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "file_extension": Path(input_path).suffix.lower()
            },
            "extraction_metadata": {
                "extraction_timestamp": datetime.datetime.now().isoformat(),
                "extractor_version": "Modular STP Extractor v1.0",
                "opencascade_available": self.opencascade_processor.opencascade_available,
                "cascadio_available": self.web_converter.cascadio_available,
                "extraction_mode": "modular_comprehensive"
            }
        }
    
    def _merge_opencascade_data(self, stp_data: Dict[str, Any], occ_data: OpenCASCADEData):
        """Merge OpenCASCADE data into main data structure"""
        stp_data["assembly_structure"] = occ_data.assembly_structure
        stp_data["part_data"] = occ_data.part_data
        stp_data["materials"] = occ_data.materials
        stp_data["colors"] = occ_data.colors.__dict__ if hasattr(occ_data.colors, '__dict__') else occ_data.colors
        stp_data["geometry_analysis"] = occ_data.geometry_analysis.__dict__ if hasattr(occ_data.geometry_analysis, '__dict__') else occ_data.geometry_analysis
        stp_data["relationships"] = occ_data.relationships
    
    def _generate_extraction_stats(self) -> Dict[str, Any]:
        """Generate extraction statistics"""
        return {
            "total_entities_processed": self.extraction_stats["processed_entities"],
            "errors_encountered": len(self.extraction_stats["errors"]),
            "error_list": self.extraction_stats["errors"],
            "data_types_discovered": list(self.extraction_stats["data_types_found"]),
            "extraction_success": len(self.extraction_stats["errors"]) == 0
        }
