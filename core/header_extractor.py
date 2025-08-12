"""STEP header extraction module"""

import re
from typing import Dict, Any
from model.extraction_data import HeaderData

class HeaderExtractor:
    """Extracts and parses STEP header information"""
    
    def __init__(self):
        self.header_patterns = {
            "FILE_DESCRIPTION": r"FILE_DESCRIPTION\s*\(\s*\((.*?)\)\s*,\s*'([^']*)'",
            "FILE_NAME": r"FILE_NAME\s*\(\s*'([^']*)'.*?'([^']*)'.*?'([^']*)'.*?'([^']*)'.*?'([^']*)'.*?'([^']*)'.*?\)",
            "FILE_SCHEMA": r"FILE_SCHEMA\s*\(\s*\(\s*'([^']*)'.*?\)\s*\)"
        }
    
    def extract_step_header(self, input_path: str) -> HeaderData:
        """Extract all STEP header information dynamically"""
        header_data = HeaderData()
        
        try:
            header_content = self._read_header_section(input_path)
            header_data.raw_header = header_content
            
            # Parse header content
            header_text = ' '.join(header_content)
            header_data.parsed_entities = self._parse_header_entities(header_text)
                        
        except Exception as e:
            header_data.extraction_error = str(e)
        
        return header_data
    
    def _read_header_section(self, input_path: str) -> list:
        """Read only the header section of the file"""
        header_content = []
        
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            in_header = False
            
            for line in f:
                line_stripped = line.strip()
                
                if line_stripped == 'HEADER;':
                    in_header = True
                    continue
                elif line_stripped == 'ENDSEC;' and in_header:
                    break
                elif in_header:
                    header_content.append(line_stripped)
        
        return header_content
    
    def _parse_header_entities(self, header_text: str) -> Dict[str, Any]:
        """Parse specific header entities using regex patterns"""
        parsed_entities = {}
        
        for entity_type, pattern in self.header_patterns.items():
            matches = re.findall(pattern, header_text, re.DOTALL)
            if matches:
                parsed_entities[entity_type] = matches
        
        return parsed_entities
