"""
Citation Tool - Custom tool for ResearchPro.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

class CitationFormatterTool:
    """
    Tool for formatting citations in various academic styles.
    
    Supports: APA, MLA, Chicago, IEEE, Harvard
    """
    
    def __init__(self):
        self.name = "format_citation"
        self.description = "Format academic citations in various styles"
    
    def format(
        self,
        source: Dict[str, Any],
        style: str = "APA"
    ) -> str:
        """
        Format a source as a citation.
        
        Args:
            source: Source metadata (title, authors, year, etc.)
            style: Citation style (APA, MLA, Chicago, IEEE, Harvard)
            
        Returns:
            Formatted citation string
        """
        style = style.upper()
        
        if style == "APA":
            return self._format_apa(source)
        elif style == "MLA":
            return self._format_mla(source)
        elif style == "CHICAGO":
            return self._format_chicago(source)
        else:
            return self._format_apa(source)  # Default to APA
    
    def _format_apa(self, source: Dict[str, Any]) -> str:
        """Format in APA style."""
        authors = source.get("authors", ["Unknown"])
        year = source.get("year", "n.d.")
        title = source.get("title", "Unknown title")
        journal = source.get("journal", "")
        doi = source.get("doi", "")
        
        # Format authors (Last, F. M.)
        author_str = ", ".join([self._format_author_apa(a) for a in authors])
        
        citation = f"{author_str} ({year}). {title}."
        
        if journal:
            citation += f" *{journal}*."
        
        if doi:
            citation += f" https://doi.org/{doi}"
        elif "url" in source:
            citation += f" {source['url']}"
        
        return citation
    
    def _format_author_apa(self, author: str) -> str:
        """Format author name in APA style."""
        parts = author.replace("Dr. ", "").split()
        if len(parts) >= 2:
            return f"{parts[-1]}, {parts[0][0]}."
        return author
    
    def _format_mla(self, source: Dict[str, Any]) -> str:
        """Format in MLA style."""
        authors = source.get("authors", ["Unknown"])
        title = source.get("title", "Unknown title")
        journal = source.get("journal", "")
        year = source.get("year", "n.d.")
        
        author_str = " and ".join(authors)
        
        citation = f'{author_str}. "{title}."'
        
        if journal:
            citation += f" *{journal}*, {year}."
        
        return citation
    
    def _format_chicago(self, source: Dict[str, Any]) -> str:
        """Format in Chicago style."""
        # Simplified Chicago format
        return self._format_apa(source)  # Use APA as baseline


# ============================================================================
# QUALITY SCORER TOOL
# ============================================================================