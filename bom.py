import subprocess
import os
import sys
import time
import traceback

# Paths to tools
FREECAD_CMD = r"C:\Program Files\FreeCAD 1.0\bin\FreeCADCmd.exe"
BLENDER_CMD = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
GLTF_TRANSFORM_PATH = r"C:\Users\sagarg_ithena\AppData\Roaming\npm\gltf-transform.cmd"

# Input STEP file
input_step = "model/75944_06.step"
base_name = os.path.splitext(os.path.basename(input_step))[0]

# Fixed BOM file path
bom_file = f"extracted_data/{base_name}/parts_data.json"
legacy_bom_file = f"models/{base_name}_bom.json"

# Ensure model directory exists
os.makedirs("model", exist_ok=True)

# Global logging function
def log(message, level="INFO"):
    """Enhanced logging with timestamps and levels"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "DEBUG": "🔍",
        "START": "🚀",
        "END": "🏁"
    }
    symbol = symbols.get(level, "📝")
    print(f"[{timestamp}] {symbol} {level}: {message}")

def extract_bom_data():
    """Extract detailed BOM data from STEP file"""
    log("=== STEP → BOM Extraction ===", "START")
    log(f"Input: {input_step}", "INFO")
    log(f"Output BOM: {bom_file}", "INFO")
    log(f"Legacy BOM: {legacy_bom_file}", "INFO")
    
    start_time = time.time()
    
    try:
        log("Starting FreeCAD subprocess for BOM extraction...", "INFO")
        log(f"Command: {FREECAD_CMD} bom_extraction.py {input_step}", "DEBUG")
        
        # Run FreeCAD BOM extraction with output capture
        result = subprocess.run([
            FREECAD_CMD,
            "bom_extraction.py",
            input_step  # Only pass the STEP file path
        ], capture_output=True, text=True, check=True)
        
        # Log subprocess output
        if result.stdout:
            log("FreeCAD output:", "DEBUG")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    log(f"  {line}", "DEBUG")
        
        if result.stderr:
            log("FreeCAD warnings/errors:", "WARNING")
            for line in result.stderr.strip().split('\n'):
                if line.strip():
                    log(f"  {line}", "WARNING")
        
        # Verify outputs
        log("Verifying output files...", "INFO")
        
        # Check main BOM file
        if os.path.exists(bom_file):
            bom_size = os.path.getsize(bom_file)
            log(f"Main BOM file created: {bom_file} ({bom_size:,} bytes)", "SUCCESS")
        else:
            log(f"Main BOM file not created: {bom_file}", "ERROR")
            raise FileNotFoundError(f"BOM data not created: {bom_file}")
        
        # Check legacy BOM file
        if os.path.exists(legacy_bom_file):
            legacy_size = os.path.getsize(legacy_bom_file)
            log(f"Legacy BOM file created: {legacy_bom_file} ({legacy_size:,} bytes)", "SUCCESS")
        else:
            log(f"Legacy BOM file not created: {legacy_bom_file}", "WARNING")
        
        # Read and display BOM summary
        try:
            import json
            with open(bom_file, 'r', encoding='utf-8') as f:
                bom_data = json.load(f)
            
            total_parts = bom_data.get("total_parts", 0)
            log(f"BOM Summary: {total_parts} parts extracted", "SUCCESS")
            
            # Display first few parts as example
            if bom_data.get("parts_list"):
                log("Sample parts extracted:", "INFO")
                for i, part in enumerate(bom_data["parts_list"][:3]):  # Show first 3 parts
                    part_name = part.get("name", "Unknown")
                    volume = part.get("shape_analysis", {}).get("geometry_properties", {}).get("volume", 0)
                    log(f"  Part {i+1}: {part_name} (Volume: {volume:.2f})", "INFO")
                
                if total_parts > 3:
                    log(f"  ... and {total_parts - 3} more parts", "INFO")
        
        except Exception as e:
            log(f"Could not read BOM summary: {e}", "WARNING")
        
        elapsed_time = time.time() - start_time
        log(f"BOM extraction completed in {elapsed_time:.2f} seconds", "SUCCESS")
        
    except subprocess.CalledProcessError as e:
        log(f"FreeCAD subprocess failed with return code {e.returncode}", "ERROR")
        if e.stdout:
            log(f"Subprocess stdout: {e.stdout}", "ERROR")
        if e.stderr:
            log(f"Subprocess stderr: {e.stderr}", "ERROR")
        raise
    except Exception as e:
        log(f"Error in BOM extraction: {e}", "ERROR")
        traceback.print_exc()
        raise

# Main execution
if __name__ == "__main__":
    overall_start_time = time.time()
    log("=== Enhanced STEP BOM Analysis Pipeline Started ===", "START")
    
    try:
        extract_bom_data()
        
        overall_elapsed = time.time() - overall_start_time
        log(f"Enhanced STEP BOM Analysis Pipeline completed successfully in {overall_elapsed:.2f} seconds", "SUCCESS")
        
    except Exception as e:
        log(f"Enhanced pipeline failed: {e}", "ERROR")
        sys.exit(1)
