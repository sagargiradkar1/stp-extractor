"""File structure analysis module"""

import re
from typing import Dict, Any
from model.extraction_data import FileAnalysisData

class FileAnalyzer:
    """Analyzes basic STP file structure and content"""
    
    def __init__(self):
        self.entity_pattern = re.compile(r'#(\d+)\s*=')
    
    def analyze_file_structure(self, input_path: str) -> FileAnalysisData:
        """Analyze the basic structure of the STP file"""
        analysis = FileAnalysisData()
        
        try:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_section = None
                
                for line_num, line in enumerate(f, 1):
                    analysis.line_count = line_num
                    line_stripped = line.strip()
                    
                    # Detect sections
                    if line_stripped in ['HEADER;', 'DATA;', 'ENDSEC;']:
                        current_section = self._detect_section(line_stripped)
                    
                    # Count sections and entities
                    self._count_sections_and_entities(
                        current_section, line_stripped, analysis
                    )
                    
                    # Detect content types
                    self._detect_content_types(line.upper(), analysis)
                    
                    # Stop for large files
                    if line_num > 50000:
                        analysis.file_truncated_analysis = True
                        break
                        
        except Exception as e:
            analysis.analysis_error = str(e)
        
        return analysis
    
    def _detect_section(self, line: str) -> str:
        """Detect which section we're in"""
        if line == 'HEADER;':
            return 'header'
        elif line == 'DATA;':
            return 'data'
        elif line == 'ENDSEC;':
            return None
        return None
    
    def _count_sections_and_entities(self, section: str, line: str, analysis: FileAnalysisData):
        """Count sections and entities"""
        if section == 'header':
            analysis.header_lines += 1
        elif section == 'data':
            analysis.data_lines += 1
            if self.entity_pattern.match(line):
                analysis.entity_count += 1
    
    def _detect_content_types(self, line_upper: str, analysis: FileAnalysisData):
        """Detect what types of content the file contains"""
        if 'COLOUR' in line_upper or 'COLOR' in line_upper:
            analysis.contains_colors = True
        if 'MATERIAL' in line_upper:
            analysis.contains_materials = True
        if 'ASSEMBLY' in line_upper:
            analysis.contains_assemblies = True
