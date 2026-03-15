import fitz  # PyMuPDF
import re
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document

class HierarchicalPDFParser:
    """
    Parses PDF documents to extract hierarchical structure (chapters, sections)
    metadata and associates it with text chunks.
    """
    
    def parse(self, file_path: str) -> List[Document]:
        """
        Main entry point. Extracts text and structure.
        Returns a list of LangChain Documents with rich metadata.
        """
        doc = fitz.open(file_path)
        toc = doc.get_toc()
        hierarchy = self._get_chapter_hierarchy(toc)
        
        # Group text by chapter to avoid breaking sentences across pages
        chapters_content = {}
        documents = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
                
            # Clean up text:
            text = text.strip()
            
            # 1. Strip standalone page numbers at start/end (aggressive cleaning)
            # Handles numbers followed by a newline or significant horizontal space
            text = re.sub(r'^\d+\s*(\n|\s{2,})', '', text) 
            text = re.sub(r'(\n|\s{2,})\d+$', '', text) 
            
            # 2. Fix hyphenated words broken across lines
            text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
            
            # 3. Collapse multiple whitespace/newlines to normalize paragraph breaks
            text = re.sub(r'\n{3,}', '\n\n', text)
            text = text.strip()
                
            chapter_info = self._get_metadata_for_page(hierarchy, page_num)
            chapter_title = chapter_info["chapter"]
            
            if chapter_title not in chapters_content:
                chapters_content[chapter_title] = {
                    "text": "",
                    "start_page": page_num,
                    "end_page": page_num,
                    "source": file_path.split("/")[-1],
                    "total_pages": doc.page_count,
                    "page_offsets": [] # List of (char_start, page_num)
                }
            
            # Append text and update the end page of this chapter block
            current_offset = len(chapters_content[chapter_title]["text"])
            if current_offset > 0:
                chapters_content[chapter_title]["text"] += "\n" + text
                # Account for the newline added
                chapters_content[chapter_title]["page_offsets"].append({
                    "start": current_offset + 1,
                    "page_num": page_num
                })
            else:
                chapters_content[chapter_title]["text"] = text
                chapters_content[chapter_title]["page_offsets"].append({
                    "start": 0,
                    "page_num": page_num
                })
                
            chapters_content[chapter_title]["end_page"] = page_num
            
        for chapter, data in chapters_content.items():
            metadata = {
                "source": data["source"],
                "chapter": chapter,
                "page": f"{data['start_page']}-{data['end_page']}" if data['start_page'] != data['end_page'] else data['start_page'],
                "total_pages": data["total_pages"],
                "page_offsets": data["page_offsets"]
            }
            documents.append(Document(page_content=data["text"], metadata=metadata))
            
        doc.close()
        return documents

    def _get_chapter_hierarchy(self, toc: List) -> List[Dict]:
        """Converts flat TOC list into a list of chapter objects with page ranges."""
        hierarchy = []
        if not toc:
            return hierarchy
            
        for i, entry in enumerate(toc):
            level, title, start_page = entry[0], entry[1], entry[2]
            if i < len(toc) - 1:
                end_page = toc[i+1][2] - 1
            else:
                end_page = 99999
                
            hierarchy.append({
                "level": level,
                "title": title,
                "start_page": start_page,
                "end_page": end_page
            })
        return hierarchy

    def _get_metadata_for_page(self, hierarchy: List[Dict], page_num: int) -> Dict[str, str]:
        """Finds the active chapter and section for a given page (page_num is 0-indexed)."""
        current_chapter = "General / Prologue"
        current_section = ""
        for entry in hierarchy:
            # entry["start_page"] is 1-indexed from TOC
            if entry["start_page"] <= (page_num + 1):
                if entry["level"] == 1:
                    current_chapter = entry["title"]
                    current_section = ""
                elif entry["level"] > 1:
                    current_section = entry["title"]
            else:
                break
        return {"chapter": current_chapter, "section": current_section}
