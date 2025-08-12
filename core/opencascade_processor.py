"""Main OpenCASCADE processing module"""

from typing import Dict, Any, Optional
from model.extraction_data import OpenCASCADEData
from .color_extractor import ColorExtractor
from .geometry_analyzer import GeometryAnalyzer
from .assembly_extractor import AssemblyExtractor

class OpenCASCADEProcessor:
    """Main coordinator for OpenCASCADE processing"""
    
    def __init__(self):
        self.opencascade_available = self._check_opencascade()
        self.reader = None
        self.app = None
        self.doc = None
        
        if self.opencascade_available:
            self._initialize_opencascade()
        
        # Initialize sub-processors
        self.color_extractor = ColorExtractor()
        self.geometry_analyzer = GeometryAnalyzer()
        self.assembly_extractor = AssemblyExtractor()
    
    def _check_opencascade(self) -> bool:
        """Check if OpenCASCADE is available"""
        try:
            from OCC.Core.STEPControl import STEPControl_Reader
            from OCC.Core.XCAFApp import XCAFApp_Application
            from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
            return True
        except ImportError:
            return False
    
    def _initialize_opencascade(self):
        """Initialize OpenCASCADE components"""
        try:
            from OCC.Core.XCAFApp import XCAFApp_Application
            from OCC.Core.TDocStd import TDocStd_Document
            from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
            
            self.reader = STEPCAFControl_Reader()
            self.app = XCAFApp_Application.GetApplication()
            self.doc = TDocStd_Document("XCAF")
            self.app.NewDocument("MDTV-XCAF", self.doc)
        except Exception as e:
            print(f"❌ OpenCASCADE initialization failed: {str(e)}")
            self.opencascade_available = False
    
    def extract_with_opencascade(self, input_path: str) -> OpenCASCADEData:
        """Extract comprehensive data using OpenCASCADE"""
        occ_data = OpenCASCADEData()
        
        if not self.opencascade_available:
            occ_data.opencascade_error = "OpenCASCADE not available"
            return occ_data
        
        try:
            from OCC.Core.IFSelect import IFSelect_RetDone
            from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool
            
            # Read STEP file
            status = self.reader.ReadFile(input_path)
            if status != IFSelect_RetDone:
                raise Exception("Failed to read STEP file with OpenCASCADE")
            
            # Transfer to document
            self.reader.Transfer(self.doc)
            
            # Get all tools
            shape_tool = XCAFDoc_DocumentTool.ShapeTool(self.doc.Main())
            color_tool = XCAFDoc_DocumentTool.ColorTool(self.doc.Main())
            material_tool = XCAFDoc_DocumentTool.MaterialTool(self.doc.Main())
            
            # Extract using specialized modules
            occ_data.assembly_structure = self.assembly_extractor.extract_assembly_tree(shape_tool, color_tool)
            occ_data.part_data = self.assembly_extractor.extract_all_parts(shape_tool, color_tool)
            occ_data.colors = self.color_extractor.extract_all_colors(color_tool, shape_tool)
            occ_data.geometry_analysis = self.geometry_analyzer.analyze_all_geometry(shape_tool)
            
            # Extract materials and relationships (basic implementation)
            occ_data.materials = {"extraction_note": "Material extraction requires specific STEP content"}
            occ_data.relationships = {"extraction_note": "Relationship extraction requires detailed analysis"}
            
        except Exception as e:
            occ_data.opencascade_error = str(e)
        
        return occ_data
