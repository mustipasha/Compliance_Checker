import fitz  # PyMuPDF
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
        
        documents = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if not text.strip():
                continue
                
            current_page_idx = page_num + 1
            chapter_info = self._get_metadata_for_page(hierarchy, current_page_idx)
            
            metadata = {
                "source": file_path.split("/")[-1],
                "page": page_num,
                "total_pages": doc.page_count,
                **chapter_info
            }
            
            documents.append(Document(page_content=text, metadata=metadata))
            
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
