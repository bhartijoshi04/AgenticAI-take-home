import re
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
from app.schemas.models import Section, PaperMetadata

class ChunkingService:
    """
    Service to chunk markdown text into structured sections.
    """
    
    SECTION_PATTERNS = {
        'abstract': ['abstract'],
        'introduction': ['introduction', 'intro'],
        'methodology': ['method', 'approach', 'model', 'algorithm', 'technique'],
        'results': ['result', 'finding', 'evaluation', 'experiment', 'analysis'],
        'discussion': ['discussion', 'interpret'],
        'conclusion': ['conclusion', 'summary', 'final'],
        'background': ['related', 'background', 'prior', 'previous'],
        'references': ['reference', 'bibliography', 'citation']
    }
    
    def extract_title(self, text: str) -> str:
        """Extract paper title from the beginning of the text"""
        lines = text.strip().split('\n')
        
        for line in lines[:10]:
            line = line.strip()
            if (line and 
                not line.startswith('#') and 
                not line.startswith('[') and 
                len(line) > 20 and
                not line.startswith('http')):
                
                title = re.sub(r'[#*_`]', '', line).strip()
                if title:
                    return title
        
        return "Unknown Title"
    
    def detect_section_type(self, header: str) -> str:
        """Determine the type/category of a section based on its header"""
        header_lower = header.lower()
        
        for section_type, patterns in self.SECTION_PATTERNS.items():
            if any(word in header_lower for word in patterns):
                return section_type
                
        return 'other'

    def _parse_section_header(self, line: str) -> Optional[Dict]:
        """Parse a markdown header line and extract section information"""
        header_match = re.match(r'^(#{1,6})\s*(.*)', line.strip())
        if not header_match:
            return None
            
        hashes = header_match.group(1)
        header_text = header_match.group(2).strip()
        level = len(hashes)
        
        # Extract section number if present
        section_num_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.*)', header_text)
        if section_num_match:
            section_number = section_num_match.group(1)
            section_name = section_num_match.group(2)
        else:
            section_number = None
            section_name = header_text
            
        return {
            'name': section_name,
            'number': section_number,
            'level': level
        }

    def chunk_text(self, markdown_text: str) -> Dict[str, Any]:
        """
        Chunk text and return a dictionary matching the schema structure.
        """
        lines = markdown_text.split('\n')
        sections_list = []
        current_section = None
        current_content = []
        
        # Extract title
        title = self.extract_title(markdown_text)
        paper_metadata = {'title': title}
        
        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()
            
            # Check for section headers
            section_info = self._parse_section_header(stripped)
            if section_info:
                # Save previous section
                if current_section is not None:
                    content = '\n'.join(current_content).strip()
                    if content:
                        meta = {
                            "section_type": self.detect_section_type(current_section['name']),
                            "level": current_section['level'],
                            "word_count": len(content.split()),
                            "char_count": len(content),
                            "start_line": current_section['start_line'],
                            "end_line": line_num - 1,
                            "section_number": current_section['number']
                        }
                        sections_list.append(Section(
                            section_name=current_section['name'],
                            content=content,
                            metadata=meta
                        ))
                
                # Start new section
                section_info['start_line'] = line_num
                current_section = section_info
                current_content = []
                
            elif stripped.lower().startswith('abstract') and current_section is None:
                # Handle abstract without header
                current_section = {
                    'name': 'Abstract',
                    'number': None,
                    'level': 1,
                    'start_line': line_num
                }
                current_content = []
                
            else:
                # Add to current section content
                if current_section is not None:
                    current_content.append(line)
        
        # Process the last section
        if current_section is not None:
            content = '\n'.join(current_content).strip()
            if content:
                meta = {
                    "section_type": self.detect_section_type(current_section['name']),
                    "level": current_section['level'],
                    "word_count": len(content.split()),
                    "char_count": len(content),
                    "start_line": current_section['start_line'],
                    "end_line": len(lines),
                    "section_number": current_section['number']
                }
                sections_list.append(Section(
                    section_name=current_section['name'],
                    content=content,
                    metadata=meta
                ))
        
        # Calculate stats
        total_words = sum(s.metadata.get('word_count', 0) for s in sections_list)
        total_chars = sum(s.metadata.get('char_count', 0) for s in sections_list)
        
        final_metadata = PaperMetadata(
            title=title,
            total_sections=len(sections_list),
            total_word_count=total_words,
            total_char_count=total_chars,
            extraction_timestamp=datetime.now().isoformat()
        )

        return {
            "paper_metadata": final_metadata.model_dump(),
            "sections": [s.model_dump() for s in sections_list]
        }
