import os
import io
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
import pytesseract


def extract_text_with_pymupdf(pdf_path: str, output_txt_path: str):
    """Extract text using PyMuPDF's built-in text extraction."""
    print(f"Starting PyMuPDF extraction for: {os.path.basename(pdf_path)}")
    
    doc = fitz.open(pdf_path)
    
    with open(output_txt_path, 'w', encoding='utf-8') as out_file:
        for page_number, page in enumerate(doc, start=1):
            print(f"  Processing page {page_number}/{len(doc)}...")
            
            # Get text directly from PDF
            raw_text = page.get_text()
            
            out_file.write(raw_text)
    
    doc.close()
    print(f"PyMuPDF extraction complete. Saved to: {output_txt_path}")


def extract_text_with_ocr(pdf_path: str, output_txt_path: str, dpi: int = 300):
    """Extract text using Tesseract OCR."""
    print(f"Starting Tesseract OCR extraction for: {os.path.basename(pdf_path)}")
    
    # Optional: Set the Tesseract binary path if needed (for Apple Silicon)
    try:
        pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
    except:
        pass  # Use system default if path doesn't exist
    
    doc = fitz.open(pdf_path)
    
    with open(output_txt_path, 'w', encoding='utf-8') as out_file:
        for page_number, page in enumerate(doc, start=1):
            print(f"  Processing page {page_number}/{len(doc)} with OCR...")
            
            try:
                # Convert page to high-resolution image
                pix = page.get_pixmap(dpi=dpi)
                img_bytes = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_bytes))
                
                # Apply OCR with better configuration
                custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
                text = pytesseract.image_to_string(image, config=custom_config)
                
                out_file.write(text.strip())
                
            except Exception as e:
                print(f"  Warning: Error processing page {page_number}: {e}")
    
    doc.close()
    print(f"Tesseract OCR extraction complete. Saved to: {output_txt_path}")


def process_pdf_with_dual_extraction(pdf_path: str, output_dir: str = None):
    """
    Extract text from a PDF using both methods and save to separate files.
    
    Args:
        pdf_path: Path to the input PDF file
        output_dir: Directory to save output files (defaults to same as PDF)
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    # Set output directory
    if output_dir is None:
        output_dir = pdf_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filenames
    base_name = pdf_path.stem
    pymupdf_output = output_dir / f"{base_name}_pymupdf_extraction.txt"
    tesseract_output = output_dir / f"{base_name}_tesseract_extraction.txt"
    
    print(f"\nStarting dual extraction for: {pdf_path.name}")
    print(f"Output directory: {output_dir}")
    print("-" * 60)
    
    # Extract using both methods
    try:
        extract_text_with_pymupdf(str(pdf_path), str(pymupdf_output))
    except Exception as e:
        print(f"PyMuPDF extraction failed: {e}")
    
    try:
        extract_text_with_ocr(str(pdf_path), str(tesseract_output))
    except Exception as e:
        print(f"Tesseract extraction failed: {e}")
    
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    
    # Show file sizes for comparison
    if pymupdf_output.exists():
        pymupdf_size = pymupdf_output.stat().st_size
        print(f"PyMuPDF output:  {pymupdf_output.name} ({pymupdf_size:,} bytes)")
    
    if tesseract_output.exists():
        tesseract_size = tesseract_output.stat().st_size
        print(f"Tesseract output: {tesseract_output.name} ({tesseract_size:,} bytes)")
    
    print(f"\nTip: Compare the files to see which method works better for your PDF quality!")


def process_pdf_directory(folder_path: str, output_dir: str = None):
    """Process all PDFs in a folder with both extraction methods."""
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"Error: Folder not found: {folder_path}")
        return
    
    pdf_files = list(folder_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in: {folder_path}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n{'='*80}")
        print(f"Processing {i}/{len(pdf_files)}: {pdf_file.name}")
        print('='*80)
        process_pdf_with_dual_extraction(str(pdf_file), output_dir)




if __name__ == "__main__":
    
    # Configuration for batch processing
    pdf_folder = "/Users/user/programming/manifestos_and_identity/1_manifesto_files/pdf"
    output_directory = "/Users/user/programming/manifestos_and_identity/2a_text_output_files"
    
    # Batch process all PDFs in the folder
    process_pdf_directory(pdf_folder, output_directory)

    