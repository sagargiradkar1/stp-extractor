"""Enhanced geometry analysis module"""

from typing import Dict, Any
from model.extraction_data import GeometryAnalysisData

class GeometryAnalyzer:
    """Analyzes geometry properties and features"""
    
    def __init__(self):
        self.opencascade_available = self._check_opencascade()
    
    def _check_opencascade(self) -> bool:
        """Check if OpenCASCADE is available"""
        try:
            from OCC.Core.GProp import GProp_GProps
            return True
        except ImportError:
            return False
    
    def analyze_all_geometry(self, shape_tool) -> GeometryAnalysisData:
        """Complete geometry analysis implementation"""
        geometry_analysis = GeometryAnalysisData()
        
        if not self.opencascade_available:
            geometry_analysis.extraction_error = "OpenCASCADE not available"
            return geometry_analysis
        
        try:
            from OCC.Core.TDF import TDF_LabelSequence
            from OCC.Core.GProp import GProp_GProps
            from OCC.Core.BRepGProp import BRepGProp_VolumeProperties, BRepGProp_Face
            from OCC.Core.TopExp import TopExp_Explorer
            from OCC.Core.TopAbs import TopAbs_FACE
            from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Sphere
            from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
            
            free_shapes = TDF_LabelSequence()
            shape_tool.GetFreeShapes(free_shapes)
            
            # Initialize analysis data
            total_volume = 0.0
            total_surface_area = 0.0
            feature_counts = {
                "planes": 0,
                "cylinders": 0, 
                "spheres": 0,
                "complex_surfaces": 0
            }
            
            # Analyze each shape
            for i in range(1, free_shapes.Length() + 1):
                label = free_shapes.Value(i)
                shape = shape_tool.GetShape(label)
                
                if not shape.IsNull():
                    # Calculate volume and surface area
                    volume, surface_area = self._calculate_properties(shape)
                    total_volume += volume
                    total_surface_area += surface_area
                    
                    # Analyze surface types
                    self._analyze_surface_types(shape, feature_counts)
            
            # Compose final analysis
            geometry_analysis.overall_statistics = {
                "total_volume": total_volume,
                "total_surface_area": total_surface_area,
                "total_shapes": free_shapes.Length()
            }
            
            geometry_analysis.complexity_metrics = {
                "surface_type_distribution": feature_counts,
                "geometric_complexity_score": sum(feature_counts.values())
            }
            
            geometry_analysis.geometric_features = list(feature_counts.keys())
            
        except Exception as e:
            geometry_analysis.extraction_error = str(e)
        
        return geometry_analysis
    
    def _calculate_properties(self, shape) -> tuple:
        """Calculate volume and surface area for a shape"""
        try:
            from OCC.Core.GProp import GProp_GProps
            from OCC.Core.BRepGProp import BRepGProp_VolumeProperties, BRepGProp_Face
            
            # Volume calculation
            volume_props = GProp_GProps()
            BRepGProp_VolumeProperties(shape, volume_props)
            volume = volume_props.Mass()
            
            # Surface area calculation
            surface_props = GProp_GProps()
            BRepGProp_Face(shape, surface_props)
            surface_area = surface_props.Mass()
            
            return volume, surface_area
        except Exception:
            return 0.0, 0.0
    
    def _analyze_surface_types(self, shape, feature_counts: Dict[str, int]):
        """Analyze and count different surface types"""
        try:
            from OCC.Core.TopExp import TopExp_Explorer
            from OCC.Core.TopAbs import TopAbs_FACE
            from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Sphere
            from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
            
            face_explorer = TopExp_Explorer(shape, TopAbs_FACE)
            while face_explorer.More():
                face = face_explorer.Current()
                try:
                    surface = BRepAdaptor_Surface(face)
                    surf_type = surface.GetType()
                    
                    if surf_type == GeomAbs_Plane:
                        feature_counts["planes"] += 1
                    elif surf_type == GeomAbs_Cylinder:
                        feature_counts["cylinders"] += 1
                    elif surf_type == GeomAbs_Sphere:
                        feature_counts["spheres"] += 1
                    else:
                        feature_counts["complex_surfaces"] += 1
                except:
                    feature_counts["complex_surfaces"] += 1
                    
                face_explorer.Next()
        except Exception:
            pass
