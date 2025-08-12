"""Main entry point for the modular STP extractor"""

import os
from pathlib import Path
from extractors.main_extractor import MainExtractor

def main():
    """Main function to run the STP extractor"""
    # Setup directories
    input_dir = Path("model")
    output_dir = Path("extracted_data")
    
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Find STP files
    stp_files = list(input_dir.glob("*.step"))
    
    if not stp_files:
        print("❌ No STP files found in 'model' folder")
        return
    
    print(f"Found {len(stp_files)} STP file(s) to process:")
    for file in stp_files:
        print(f"  - {file.name}")
    
    # Initialize extractor
    extractor = MainExtractor()
    
    # Process each file
    for stp_file in stp_files:
        print(f"\n🔄 Processing: {stp_file.name}")
        
        # Create output subdirectory
        model_output_dir = output_dir / stp_file.stem
        model_output_dir.mkdir(exist_ok=True)
        
        try:
            # Extract all data
            result = extractor.extract_all_stp_data(str(stp_file), str(model_output_dir))
            print(f"✅ Extraction complete for: {stp_file.name}")
            
        except Exception as e:
            print(f"❌ Failed to process {stp_file.name}: {str(e)}")

if __name__ == "__main__":
    main()
