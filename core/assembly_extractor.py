"""Assembly structure extraction module"""

from typing import Dict, Any, Optional
from model.extraction_data import OpenCASCADEData

class AssemblyExtractor:
    """Extracts assembly structure and part data from STEP files"""
    
    def __init__(self):
        self.opencascade_available = self._check_opencascade()
    
    def _check_opencascade(self) -> bool:
        """Check if OpenCASCADE is available"""
        try:
            from OCC.Core.TDF import TDF_LabelSequence
            return True
        except ImportError:
            return False
    
    def extract_assembly_tree(self, shape_tool, color_tool) -> Dict[str, Any]:
        """Extract complete assembly hierarchy"""
        if not self.opencascade_available:
            return {"extraction_error": "OpenCASCADE not available"}
        
        try:
            from OCC.Core.TDF import TDF_LabelSequence
            
            free_shapes = TDF_LabelSequence()
            shape_tool.GetFreeShapes(free_shapes)
            
            assembly_tree = {
                "root_assemblies": [],
                "total_free_shapes": free_shapes.Length(),
                "hierarchy_depth": 0
            }
            
            for i in range(1, free_shapes.Length() + 1):
                label = free_shapes.Value(i)
                assembly_node = self._process_assembly_node(label, shape_tool, color_tool, 0)
                assembly_tree["root_assemblies"].append(assembly_node)
                
                # Calculate max depth
                node_depth = self._calculate_node_depth(assembly_node)
                assembly_tree["hierarchy_depth"] = max(assembly_tree["hierarchy_depth"], node_depth)
            
            return assembly_tree
            
        except Exception as e:
            return {"extraction_error": str(e)}
    
    def extract_all_parts(self, shape_tool, color_tool) -> Dict[str, Any]:
        """Extract all parts with comprehensive data"""
        parts_data = {
            "total_parts": 0,
            "parts_list": []
        }
        
        if not self.opencascade_available:
            parts_data["extraction_error"] = "OpenCASCADE not available"
            return parts_data
        
        try:
            from OCC.Core.TDF import TDF_LabelSequence
            
            free_shapes = TDF_LabelSequence()
            shape_tool.GetFreeShapes(free_shapes)
            
            for i in range(1, free_shapes.Length() + 1):
                label = free_shapes.Value(i)
                if shape_tool.IsSimpleShape(label):
                    part_data = {
                        "part_id": f"part_{i:04d}",
                        "label_id": str(label),
                        "name": self._extract_label_name(label),
                        "shape_analysis": {},
                        "color_data": {},
                        "custom_properties": {}
                    }
                    
                    # Get shape and analyze
                    shape = shape_tool.GetShape(label)
                    if not shape.IsNull():
                        part_data["shape_analysis"] = self._analyze_shape_comprehensive(shape)
                    
                    # Get color
                    part_data["color_data"] = self._extract_label_color(label, color_tool)
                    
                    # Get custom properties
                    part_data["custom_properties"] = self._extract_label_attributes(label)
                    
                    parts_data["parts_list"].append(part_data)
                    parts_data["total_parts"] += 1
                    
        except Exception as e:
            parts_data["extraction_error"] = str(e)
        
        return parts_data
    
    def _process_assembly_node(self, label, shape_tool, color_tool, level):
        """Process individual assembly node with all available data"""
        node_data = {
            "label_id": str(label),
            "level": level,
            "name": self._extract_label_name(label),
            "type": "assembly" if not shape_tool.IsSimpleShape(label) else "part",
            "shape_info": {},
            "color_info": {},
            "attributes": {},
            "children": []
        }
        
        try:
            # Get shape
            shape = shape_tool.GetShape(label)
            if not shape.IsNull():
                node_data["shape_info"] = self._analyze_shape_comprehensive(shape)
            
            # Get color
            node_data["color_info"] = self._extract_label_color(label, color_tool)
            
            # Get all attributes
            node_data["attributes"] = self._extract_label_attributes(label)
            
            # Process children
            if not shape_tool.IsSimpleShape(label):
                from OCC.Core.TDF import TDF_LabelSequence
                child_labels = TDF_LabelSequence()
                if shape_tool.GetComponents(label, child_labels):
                    for j in range(1, child_labels.Length() + 1):
                        child_label = child_labels.Value(j)
                        child_node = self._process_assembly_node(child_label, shape_tool, color_tool, level + 1)
                        node_data["children"].append(child_node)
            
        except Exception as e:
            node_data["processing_error"] = str(e)
        
        return node_data
    
    def _analyze_shape_comprehensive(self, shape):
        """Comprehensive analysis of a shape"""
        analysis = {
            "topology": {},
            "geometry_properties": {},
            "bounding_info": {},
            "shape_type": str(shape.ShapeType()) if hasattr(shape, 'ShapeType') else "unknown",
            "is_valid": True
        }
        
        try:
            from OCC.Core.TopExp import TopExp_Explorer
            from OCC.Core.TopAbs import (TopAbs_VERTEX, TopAbs_EDGE, TopAbs_FACE, 
                                        TopAbs_SOLID, TopAbs_SHELL, TopAbs_WIRE, TopAbs_COMPOUND)
            from OCC.Core.GProp import GProp_GProps
            from OCC.Core.BRepGProp import BRepGProp_VolumeProperties, BRepGProp_Face
            from OCC.Core.Bnd import Bnd_Box
            from OCC.Core.BRepBndLib import BRepBndLib_Add
            
            # Topology analysis
            topology_types = [
                (TopAbs_VERTEX, "vertices"),
                (TopAbs_EDGE, "edges"),
                (TopAbs_FACE, "faces"),
                (TopAbs_SOLID, "solids"),
                (TopAbs_SHELL, "shells"),
                (TopAbs_WIRE, "wires"),
                (TopAbs_COMPOUND, "compounds")
            ]
            
            for topo_type, key in topology_types:
                explorer = TopExp_Explorer(shape, topo_type)
                count = 0
                while explorer.More():
                    count += 1
                    explorer.Next()
                analysis["topology"][key] = count
            
            # Geometry properties
            try:
                props = GProp_GProps()
                BRepGProp_VolumeProperties(shape, props)
                
                volume = props.Mass()
                com = props.CentreOfMass()
                
                analysis["geometry_properties"] = {
                    "volume": volume,
                    "center_of_mass": [com.X(), com.Y(), com.Z()],
                    "has_inertia_data": True
                }
                
                # Surface area
                surface_props = GProp_GProps()
                BRepGProp_Face(shape, surface_props)
                analysis["geometry_properties"]["surface_area"] = surface_props.Mass()
                
            except Exception as e:
                analysis["geometry_properties"] = {"calculation_failed": str(e)}
            
            # Bounding box
            try:
                bbox = Bnd_Box()
                BRepBndLib_Add(shape, bbox)
                x_min, y_min, z_min, x_max, y_max, z_max = bbox.Get()
                
                analysis["bounding_info"] = {
                    "min_point": [x_min, y_min, z_min],
                    "max_point": [x_max, y_max, z_max],
                    "dimensions": [x_max - x_min, y_max - y_min, z_max - z_min],
                    "center": [(x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2]
                }
            except Exception as e:
                analysis["bounding_info"] = {"calculation_failed": str(e)}
                
        except Exception as e:
            analysis["analysis_error"] = str(e)
        
        return analysis
    
    def _extract_label_name(self, label):
        """Extract name from label"""
        try:
            from OCC.Core.TDataStd import TDataStd_Name
            name_attr = TDataStd_Name()
            if label.FindAttribute(TDataStd_Name.GetID(), name_attr):
                return name_attr.Get().ToExtString()
            else:
                return f"Unnamed_{str(label)}"
        except Exception:
            return f"Label_{str(label)}"
    
    def _extract_label_color(self, label, color_tool):
        """Extract color from label"""
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
    
    def _extract_label_attributes(self, label):
        """Extract all attributes from label"""
        attributes = {}
        
        try:
            from OCC.Core.TDataStd import TDataStd_Comment
            # Extract comments
            comment_attr = TDataStd_Comment()
            if label.FindAttribute(TDataStd_Comment.GetID(), comment_attr):
                attributes["comment"] = comment_attr.Get().ToExtString()
            
        except Exception:
            attributes["attribute_extraction_error"] = True
        
        return attributes
    
    def _calculate_node_depth(self, node):
        """Calculate depth of assembly node"""
        if not node.get("children"):
            return node.get("level", 0)
        
        max_child_depth = 0
        for child in node["children"]:
            child_depth = self._calculate_node_depth(child)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
