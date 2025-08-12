"""Web format conversion module"""

import os
from typing import Dict, Any
from model.extraction_data import WebAssetsData

class WebConverter:
    """Converts STP files to web-ready formats"""
    
    def __init__(self):
        self.cascadio_available = self._check_cascadio()
    
    def _check_cascadio(self) -> bool:
        """Check if cascadio is available"""
        try:
            import cascadio
            return True
        except ImportError:
            return False
    
    def convert_to_web_format(self, input_path: str, output_dir: str) -> WebAssetsData:
        """Convert to web-ready format"""
        web_assets = WebAssetsData()
        
        if not self.cascadio_available:
            web_assets.conversion_unavailable = "Cascadio not installed"
            return web_assets
        
        try:
            import cascadio
            
            glb_path = os.path.join(output_dir, "model.glb")
            cascadio.step_to_glb(input_path, glb_path)
            
            web_assets.glb_file = "model.glb"
            web_assets.file_size = os.path.getsize(glb_path)
            web_assets.format = "GLB"
            web_assets.three_js_compatible = True
            
        except Exception as e:
            web_assets.conversion_error = str(e)
        
        return web_assets
