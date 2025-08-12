import sys
import Part
import json
import os
import FreeCAD

print("Arguments: " + str(sys.argv))

# Get step file argument
step_file = sys.argv[-1]

print("Processing BOM extraction for: " + step_file)

# Create FreeCAD document for BOM extraction
doc = FreeCAD.newDocument()

try:
    # Load STEP file into FreeCAD document
    Part.insert(step_file, doc.Name)
    print("SUCCESS: Loaded " + str(len(doc.Objects)) + " objects for BOM extraction")
    
    # Extract BOM data in Three.js viewer compatible format
    bom_data = {
        "total_parts": 0,
        "parts_list": []
    }
    
    valid_parts = []
    part_counter = 0
    
    # Process each object for BOM
    for obj in doc.Objects:
        # More lenient shape checking
        if hasattr(obj, 'Shape') and obj.Shape and not obj.Shape.isNull():
            try:
                part_counter += 1
                part_id = "part_" + str(part_counter).zfill(4)
                
                # Initialize properties
                volume = 0.0
                surface_area = 0.0
                center_of_mass = [0.0, 0.0, 0.0]
                dimensions = [0.0, 0.0, 0.0]
                
                # Safe volume extraction
                try:
                    volume = float(obj.Shape.Volume) if hasattr(obj.Shape, 'Volume') else 0.0
                except:
                    volume = 0.0
                
                # Safe surface area extraction  
                try:
                    surface_area = float(obj.Shape.Area) if hasattr(obj.Shape, 'Area') else 0.0
                except:
                    surface_area = 0.0
                
                # Safe center of mass extraction
                try:
                    if hasattr(obj.Shape, 'CenterOfMass'):
                        center_of_mass = [
                            float(obj.Shape.CenterOfMass.x),
                            float(obj.Shape.CenterOfMass.y),
                            float(obj.Shape.CenterOfMass.z)
                        ]
                except:
                    center_of_mass = [0.0, 0.0, 0.0]
                
                # Safe bounding box extraction
                try:
                    if hasattr(obj.Shape, 'BoundBox'):
                        dimensions = [
                            float(obj.Shape.BoundBox.XLength),
                            float(obj.Shape.BoundBox.YLength),
                            float(obj.Shape.BoundBox.ZLength)
                        ]
                except:
                    dimensions = [0.0, 0.0, 0.0]
                
                # Safe topology extraction
                vertices = 0
                edges = 0
                faces = 0
                solids = 0
                
                try:
                    vertices = len(obj.Shape.Vertexes) if hasattr(obj.Shape, 'Vertexes') else 0
                    edges = len(obj.Shape.Edges) if hasattr(obj.Shape, 'Edges') else 0
                    faces = len(obj.Shape.Faces) if hasattr(obj.Shape, 'Faces') else 0
                    solids = len(obj.Shape.Solids) if hasattr(obj.Shape, 'Solids') else 1
                except:
                    vertices = edges = faces = solids = 0
                
                # Create comprehensive part info
                part_info = {
                    "part_id": part_id,
                    "name": getattr(obj, 'Label', 'Part_' + str(part_counter)),
                    "shape_analysis": {
                        "topology": {
                            "vertices": vertices,
                            "edges": edges,
                            "faces": faces,
                            "solids": max(solids, 1)  # Ensure at least 1 solid
                        },
                        "geometry_properties": {
                            "volume": volume,
                            "surface_area": surface_area,
                            "center_of_mass": center_of_mass
                        },
                        "bounding_info": {
                            "dimensions": dimensions
                        },
                        "shape_type": "2",  # Default shape type
                        "is_valid": True
                    },
                    "color_data": {
                        "has_color": True,
                        "type": "surface",
                        "rgb": [
                            # Generate varied colors based on part index for visual distinction
                            round(0.3 + (part_counter * 0.1) % 0.7, 2),
                            round(0.3 + (part_counter * 0.15) % 0.7, 2), 
                            round(0.3 + (part_counter * 0.2) % 0.7, 2)
                        ]
                    },
                    "custom_properties": {
                        "type": getattr(obj, 'TypeId', 'Part::Feature')
                    }
                }
                
                # Add hex color conversion
                rgb = part_info["color_data"]["rgb"]
                part_info["color_data"]["hex"] = "#{:02x}{:02x}{:02x}".format(
                    int(rgb[0] * 255), 
                    int(rgb[1] * 255), 
                    int(rgb[2] * 255)
                )
                
                # Try to extract actual color if available
                try:
                    if hasattr(obj, 'ViewObject') and hasattr(obj.ViewObject, 'ShapeColor'):
                        actual_color = obj.ViewObject.ShapeColor
                        if actual_color and len(actual_color) >= 3:
                            part_info["color_data"]["rgb"] = [
                                float(actual_color[0]),
                                float(actual_color[1]), 
                                float(actual_color[2])
                            ]
                            part_info["color_data"]["hex"] = "#{:02x}{:02x}{:02x}".format(
                                int(actual_color[0] * 255),
                                int(actual_color[1] * 255),
                                int(actual_color[2] * 255)
                            )
                except:
                    pass  # Use generated colors as fallback
                
                # Add the part to the list
                bom_data["parts_list"].append(part_info)
                valid_parts.append((obj, part_info))
                
                print("Added part " + str(part_counter) + ": " + part_info["name"] + " (Volume: " + str(volume) + ")")
                
            except Exception as e:
                print("Warning: Error processing object " + str(part_counter) + ": " + str(e))
                continue
    
    bom_data["total_parts"] = part_counter
    print("SUCCESS: Extracted BOM data: " + str(part_counter) + " parts")
    
    # Save enhanced BOM data as JSON
    base_name = os.path.splitext(os.path.basename(step_file))[0]
    
    # Create extracted_data directory structure for Three.js viewer
    extracted_dir = "extracted_data/" + base_name
    os.makedirs(extracted_dir, exist_ok=True)
    
    # Save parts_data.json for Three.js viewer
    parts_data_file = extracted_dir + "/parts_data.json"
    with open(parts_data_file, 'w', encoding='utf-8') as f:
        json.dump(bom_data, f, indent=2, ensure_ascii=False)
    print("SUCCESS: Enhanced BOM data saved: " + parts_data_file)
    
    # Also save in models directory for backward compatibility
    os.makedirs("models", exist_ok=True)
    bom_file = "models/" + base_name + "_bom.json"
    with open(bom_file, 'w', encoding='utf-8') as f:
        json.dump(bom_data, f, indent=2, ensure_ascii=False)
    print("SUCCESS: Legacy BOM data saved: " + bom_file)

except Exception as e:
    print("ERROR in BOM extraction: " + str(e))
    import traceback
    traceback.print_exc()
    raise
finally:
    # Clean up FreeCAD document
    try:
        FreeCAD.closeDocument(doc.Name)
    except:
        pass

print("SUCCESS: BOM extraction completed successfully")
