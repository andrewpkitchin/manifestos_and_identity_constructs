
import re
from pathlib import Path
from b_text_cleaning import TextCleaner
from b_text_cleaning import clean_manifesto_file

def compare_extraction_methods(pymupdf_file: str, tesseract_file: str, output_dir: str = None):
    """Clean both extraction methods and help choose the better one."""
    pymupdf_path = Path(pymupdf_file)
    tesseract_path = Path(tesseract_file)
    
    if output_dir is None:
        output_dir = pymupdf_path.parent / "comparison"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Cleaning both extraction methods for comparison...")
    print("=" * 60)
    
    # Clean both files
    pymupdf_cleaned = clean_manifesto_file(
        str(pymupdf_path), 
        str(output_dir / f"{pymupdf_path.stem}_cleaned.txt")
    )
    
    tesseract_cleaned = clean_manifesto_file(
        str(tesseract_path), 
        str(output_dir / f"{tesseract_path.stem}_cleaned.txt")
    )
    
    # Basic comparison metrics
    if pymupdf_cleaned and tesseract_cleaned:
        with open(pymupdf_cleaned, 'r', encoding='utf-8') as f:
            pymupdf_text = f.read()
        with open(tesseract_cleaned, 'r', encoding='utf-8') as f:
            tesseract_text = f.read()
        
        print(f"\nCOMPARISON RESULTS:")
        print(f"PyMuPDF cleaned length: {len(pymupdf_text):,} characters")
        print(f"Tesseract cleaned length: {len(tesseract_text):,} characters")
        print(f"PyMuPDF word count: {len(pymupdf_text.split()):,}")
        print(f"Tesseract word count: {len(tesseract_text.split()):,}")
        
        # Simple quality heuristic
        pymupdf_quality = len([w for w in pymupdf_text.split() if len(w) > 2])
        tesseract_quality = len([w for w in tesseract_text.split() if len(w) > 2])
        
        print(f"\nQuality heuristic (words > 2 chars):")
        print(f"PyMuPDF: {pymupdf_quality:,}")
        print(f"Tesseract: {tesseract_quality:,}")
        
        # Count OCR-like errors
        ocr_error_patterns = [r'\bl[sf]\b', r'\bln\b', r'\blt\b', r'\b[0-9]([a-z]+)\b', r'\b([a-z]+)[0-9]\b']
        pymupdf_errors = sum(len(re.findall(pattern, pymupdf_text, re.IGNORECASE)) for pattern in ocr_error_patterns)
        tesseract_errors = sum(len(re.findall(pattern, tesseract_text, re.IGNORECASE)) for pattern in ocr_error_patterns)
        
        print(f"\nOCR-like errors detected:")
        print(f"PyMuPDF: {pymupdf_errors}")
        print(f"Tesseract: {tesseract_errors}")
        
        if pymupdf_quality > tesseract_quality and pymupdf_errors <= tesseract_errors:
            print("\nRecommendation: PyMuPDF extraction appears cleaner")
        elif tesseract_quality > pymupdf_quality and tesseract_errors <= pymupdf_errors:
            print("\nRecommendation: Tesseract extraction appears cleaner")
        else:
            print("\nRecommendation: Manual review needed - results are mixed")




if __name__ == "__main__":
    compare_extraction_methods("2_2_cleaned_text_files/Vote Leave - Why Vote Leave_pymupdf_extraction_cleaned.txt","2_2_cleaned_text_files/Vote Leave - Why Vote Leave_tesseract_extraction_cleaned.txt")