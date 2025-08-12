"""Enhanced color extraction module"""

from typing import Dict, Any, Optional
from model.extraction_data import ColorData

class ColorExtractor:
    """Extracts color information from STP files using OpenCASCADE"""
    
    def __init__(self):
        self.opencascade_available = self._check_opencascade()
    
    def _check_opencascade(self) -> bool:
        """Check if OpenCASCADE is available"""
        try:
            from OCC.Core.Quantity import Quantity_Color
            return True
        except ImportError:
            return False
    
    def extract_all_colors(self, color_tool, shape_tool) -> ColorData:
        """Enhanced color extraction using proper OpenCASCADE methods"""
        colors = ColorData()
        
        if not self.opencascade_available:
            colors.extraction_error = "OpenCASCADE not available"
            return colors
        
        try:
            from OCC.Core.TDF import TDF_LabelSequence
            from OCC.Core.Quantity import Quantity_Color
            from OCC.Core.XCAFDoc import XCAFDoc_ColorGen, XCAFDoc_ColorSurf, XCAFDoc_ColorCurv
            
            # Extract colors from color tool
            self._extract_from_color_tool(color_tool, colors)
            
            # Extract colors from shapes
            self._extract_from_shapes(shape_tool, color_tool, colors)
            
        except Exception as e:
            colors.extraction_error = str(e)
        
        return colors
    
    def _extract_from_color_tool(self, color_tool, colors: ColorData):
        """Extract colors directly from color tool"""
        from OCC.Core.TDF import TDF_LabelSequence
        from OCC.Core.Quantity import Quantity_Color
        from OCC.Core.XCAFDoc import XCAFDoc_ColorGen, XCAFDoc_ColorSurf, XCAFDoc_ColorCurv
        
        # Get all labels that have colors assigned
        color_labels = TDF_LabelSequence()
        color_tool.GetColors(color_labels)
        
        for i in range(1, color_labels.Length() + 1):
            label = color_labels.Value(i)
            color = Quantity_Color()
            
            # Try different color types
            color_type = None
            if color_tool.GetColor(label, XCAFDoc_ColorGen, color):
                color_type = "general"
            elif color_tool.GetColor(label, XCAFDoc_ColorSurf, color):
                color_type = "surface"  
            elif color_tool.GetColor(label, XCAFDoc_ColorCurv, color):
                color_type = "curve"
            
            if color_type:
                color_data = {
                    "type": color_type,
                    "rgb": [color.Red(), color.Green(), color.Blue()],
                    "hex": f"#{int(color.Red()*255):02x}{int(color.Green()*255):02x}{int(color.Blue()*255):02x}",
                    "label_id": str(label)
                }
                
                colors.color_definitions.append(color_data)
                colors.color_assignments[str(label)] = color_data
                colors.total_colors += 1
    
    def _extract_from_shapes(self, shape_tool, color_tool, colors: ColorData):
        """Extract colors from shape labels"""
        from OCC.Core.TDF import TDF_LabelSequence
        from OCC.Core.XCAFDoc import XCAFDoc_ColorGen
        
        free_shapes = TDF_LabelSequence()
        shape_tool.GetFreeShapes(free_shapes)
        
        for i in range(1, free_shapes.Length() + 1):
            label = free_shapes.Value(i)
            
            # Check if shape has color assigned
            if color_tool.IsSet(label, XCAFDoc_ColorGen):
                if str(label) not in colors.color_assignments:
                    color_info = self._extract_label_color(label, color_tool)
                    if color_info and color_info.get("has_color"):
                        colors.color_assignments[str(label)] = color_info
                        colors.total_colors += 1
    
    def _extract_label_color(self, label, color_tool) -> Optional[Dict[str, Any]]:
        """Extract color from a specific label"""
        try:
            from OCC.Core.Quantity import Quantity_Color
            
            color = Quantity_Color()
            if color_tool.GetColor(label, color):
                return {
                    "has_color": True,
                    "rgb": [color.Red(), color.Green(), color.Blue()],
                    "hex": f"#{int(color.Red()*255):02x}{int(color.Green()*255):02x}{int(color.Blue()*255):02x}"
                }
            else:
                return {"has_color": False}
        except Exception:
            return {"color_extraction_error": True}
