# core/pdf_processor.py
import fitz  # PyMuPDF
import io
from typing import List, Tuple, Optional

"""
This module handles the low-level interactions with PDF files using PyMuPDF.
It is responsible for loading, searching, redacting, and saving PDFs.
Processing is done in-memory to enhance security.
"""

def search_text_in_page(page: fitz.Page, patterns: dict) -> dict:
    """Searches for text matching given regex patterns on a single page."""
    found_instances = {key: [] for key in patterns.keys()}
    for key, pattern in patterns.items():
        text_instances = page.search_for(pattern.pattern, quads=True)
        if text_instances:
            found_instances[key].extend(text_instances)
    return found_instances

def search_images_in_page(page: fitz.Page) -> List[fitz.Rect]:
    """Finds all images on a page and returns their bounding boxes."""
    image_instances = [fitz.Rect(img[0:4]) for img in page.get_images(full=True)]
    return image_instances

def apply_redactions(page: fitz.Page, instances: List[fitz.Quad], placeholder: str, fill_color: Tuple[float, float, float]):
    """Applies redaction annotations to a page for given instances."""
    for inst in instances:
        page.add_redact_annot(inst, text=placeholder, fill=fill_color, text_color=(1,1,1))
    page.apply_redactions()

def process_pdf_in_memory(
    file_bytes: bytes,
    redaction_map: dict,
    page_range: Optional[Tuple[int, int]] = None,
    custom_texts: Optional[List[str]] = None
) -> bytes:
    """
    Loads a PDF from bytes, applies various redactions, and returns the redacted PDF as bytes.
    
    Args:
        file_bytes: The byte content of the PDF file.
        redaction_map: A dictionary specifying what to redact (e.g., {"EMAIL": True, "IMAGES": False}).
        page_range: A tuple (start_page, end_page) to process. If None, all pages are processed.
        custom_texts: A list of specific user-provided strings to redact.
    
    Returns:
        The byte content of the redacted PDF.
    """
    from core.redaction_config import PII_PATTERNS, REDACTION_CONFIG

    try:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"Failed to open PDF. It may be corrupt or encrypted. Error: {e}")

    start_page, end_page = 0, len(pdf_document) - 1
    if page_range:
        start_page = max(0, page_range[0] - 1)
        end_page = min(len(pdf_document) - 1, page_range[1] - 1)

    for page_num in range(start_page, end_page + 1):
        page = pdf_document.load_page(page_num)
        all_instances_to_redact = []
        
        # 1. Gather PII instances based on regex patterns
        patterns_to_search = {key: PII_PATTERNS[key] for key, enabled in redaction_map.items() if enabled and key in PII_PATTERNS}
        if patterns_to_search:
            found_pii = search_text_in_page(page, patterns_to_search)
            all_pii_instances = [inst for instances in found_pii.values() for inst in instances]
            all_instances_to_redact.extend(all_pii_instances)

        # 2. Gather custom text instances ---
        if custom_texts:
            for text in custom_texts:
                # The search is case-sensitive. Use page.search_for(text, quads=True, flags=fitz.TEXT_SEARCH_CASE_INSENSITIVE) for case-insensitivity
                found_text_instances = page.search_for(text, quads=True)
                all_instances_to_redact.extend(found_text_instances)
        
        # 3. Gather image instances if requested
        if redaction_map.get("IMAGES", False):
            image_instances = search_images_in_page(page)
            all_instances_to_redact.extend(image_instances)

        # 4. Apply all collected redactions for the page at once
        if all_instances_to_redact:
            apply_redactions(page, all_instances_to_redact, REDACTION_CONFIG["placeholder_text"], REDACTION_CONFIG["fill_color"])

    output_buffer = io.BytesIO()
    pdf_document.save(output_buffer, garbage=4, deflate=True, clean=True)
    pdf_document.close()
    
    output_buffer.seek(0)
    return output_buffer.getvalue()