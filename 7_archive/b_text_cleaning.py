import os
import re
from pathlib import Path
from typing import List, Tuple, Dict
import string
import unicodedata


class TextCleaner:
    def __init__(self):
        # Common patterns to remove or fix
        self.noise_patterns = [
            r'[•·∙◦▪▫■□▲▼►◄]',  # Various bullet points and shapes
            r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # URLs
            r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[/\w.-]*',  # Full URLs
            r'@\s*\\?[a-zA-Z]+\s*[Ll]eave',  # Vote Leave artifacts
            r'HM Government',  # Header repetition
            r'EUReferendum\.gov\.uk',  # Specific URL artifacts
            r'voteleavetakecontrol\.org',  # Vote Leave URLs
            r'\$+_+\$*',  # Decorative lines
            r'—+',  # Long dashes
            r'=+',  # Equals signs used as separators
            r'[^\S\n]{5,}',  # Multiple spaces (5 or more)
            r'\.{4,}',  # Multiple dots (4 or more)
            r'-{4,}',  # Multiple hyphens (4 or more)
            r'_{4,}',  # Multiple underscores (4 or more)
        ]
        
        # Patterns for fragmented text that should be joined
        self.fragment_patterns = [
            r'\b([a-z])\s+([a-z])\s+([a-z])\b',  # Single letters: "a b c"
            r'\b([A-Z])\s+([a-z]+)',  # Capital letter separated from word
            r'([a-z]+)\s+([A-Z])\s+([a-z]+)',  # Word fragments
        ]
        
        # Common political/governmental terms that get fragmented
        self.term_fixes = {
            'E U': 'EU',
            'U K': 'UK',
            'N H S': 'NHS',
            'G D P': 'GDP',
            'V A T': 'VAT',
            'M P': 'MP',
            'U N': 'UN',
            'N A T O': 'NATO',
            'E E A': 'EEA',
            'U S': 'US',
            # Common OCR misreads
            'ls': 'is',  # common OCR error
            'lf': 'If',  # common OCR error at start of sentence
            'ln': 'In',  # common OCR error at start of sentence
        }
        
        # OCR-specific character replacements
        self.ocr_char_replacements = {
            '|': 'I',  # Pipe often misread for I
            '0': 'O',  # Zero for O in certain contexts
            '1': 'l',  # One for lowercase L in certain contexts
            '！': '!',  # Full-width exclamation
            '？': '?',  # Full-width question mark
            '，': ',',  # Full-width comma
            '。': '.',  # Full-width period
            ''': "'",  # Smart quotes
            ''': "'",
            '"': '"',
            '"': '"',
            '–': '-',  # En dash
            '—': '-',  # Em dash
        }

    def normalize_unicode(self, text: str) -> str:
        """Normalize unicode characters and remove non-printable characters."""
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Remove zero-width characters and other invisible unicode
        invisible_chars = [
            '\u200b',  # Zero-width space
            '\u200c',  # Zero-width non-joiner
            '\u200d',  # Zero-width joiner
            '\ufeff',  # Zero-width no-break space
            '\u2060',  # Word joiner
        ]
        for char in invisible_chars:
            text = text.replace(char, '')
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char in '\n\t' or not unicodedata.category(char).startswith('C'))
        
        return text

    def fix_ocr_character_errors(self, text: str) -> str:
        """Fix common OCR character misreads."""
        # Apply character replacements
        for wrong, right in self.ocr_char_replacements.items():
            text = text.replace(wrong, right)
        
        # Fix specific patterns
        # Fix "l" misread as "1" in common words
        text = re.sub(r'\b1ike\b', 'like', text, flags=re.IGNORECASE)
        text = re.sub(r'\b1ive\b', 'live', text, flags=re.IGNORECASE)
        text = re.sub(r'\b1ater\b', 'later', text, flags=re.IGNORECASE)
        text = re.sub(r'\b1ess\b', 'less', text, flags=re.IGNORECASE)
        
        # Fix "I" misread as "l" at start of sentences
        text = re.sub(r'(^|\. )l\b', r'\1I', text)
        
        # Fix common OCR errors with context
        text = re.sub(r'\bls\b', 'is', text)
        text = re.sub(r'\blf\b', 'If', text)
        text = re.sub(r'\bln\b', 'In', text)
        text = re.sub(r'\blt\b', 'It', text)
        text = re.sub(r'\bls\b', 'is', text)
        
        return text

    def remove_noise_patterns(self, text: str) -> str:
        """Remove common OCR artifacts and noise patterns."""
        for pattern in self.noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text

    def fix_fragmented_text(self, text: str) -> str:
        """Fix fragmented words and abbreviations."""
        # Fix known term fragmentations
        for fragmented, fixed in self.term_fixes.items():
            text = re.sub(r'\b' + fragmented + r'\b', fixed, text, flags=re.IGNORECASE)
        
        # Fix single character fragments (common OCR issue)
        text = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])\b', r'\1\2\3', text)
        
        # Fix numbers that got spaces inserted
        text = re.sub(r'\b(\d)\s+(\d)\s+(\d)\b', r'\1\2\3', text)
        text = re.sub(r'\b(\d)\s+(\d)\b', r'\1\2', text)
        
        return text

    def fix_punctuation_spacing(self, text: str) -> str:
        """Fix spacing around punctuation marks."""
        # Remove spaces before punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        # Add space after punctuation if missing (but not for decimals)
        text = re.sub(r'([.,;:!?])(?=[A-Za-z])', r'\1 ', text)
        
        # Fix decimal numbers that got spaces
        text = re.sub(r'(\d)\s+\.\s+(\d)', r'\1.\2', text)
        
        # Fix spacing around quotes
        text = re.sub(r'\s+"', ' "', text)
        text = re.sub(r'"\s+', '" ', text)
        text = re.sub(r"\s+'", " '", text)
        text = re.sub(r"'\s+", "' ", text)
        
        return text

    def normalize_spacing(self, text: str) -> str:
        """Normalize whitespace and line breaks."""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Replace multiple line breaks with double line break (paragraph separation)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Fix lines that end mid-sentence (common in PDF extraction)
        lines = text.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                cleaned_lines.append('')
                continue
                
            # If line doesn't end with punctuation and next line starts with lowercase,
            # probably should be joined
            if (i < len(lines) - 1 and 
                line and 
                not line[-1] in '.!?:;"\'' and 
                lines[i + 1].strip() and 
                lines[i + 1].strip()[0].islower()):
                line += ' '
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def remove_header_footer_repetition(self, text: str) -> str:
        """Remove repeated headers, footers, and website references."""
        lines = text.split('\n')
        
        # Find lines that appear multiple times (likely headers/footers)
        line_counts = {}
        for line in lines:
            clean_line = line.strip().lower()
            if len(clean_line) > 10:  # Only consider substantial lines
                line_counts[clean_line] = line_counts.get(clean_line, 0) + 1
        
        # Remove lines that appear more than twice (likely repetitive)
        filtered_lines = []
        seen_repetitive = set()
        
        for line in lines:
            clean_line = line.strip().lower()
            if (line_counts.get(clean_line, 0) > 2 and 
                clean_line not in seen_repetitive and
                len(clean_line) > 10):
                seen_repetitive.add(clean_line)
                continue
            elif clean_line in seen_repetitive:
                continue
            else:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)

    def fix_broken_sentences(self, text: str) -> str:
        """Attempt to fix sentences broken across lines."""
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        fixed_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            lines = paragraph.split('\n')
            fixed_lines = []
            current_sentence = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # If the current sentence doesn't end with punctuation
                # and the new line doesn't start with a capital letter,
                # they probably belong together
                if (current_sentence and 
                    not current_sentence[-1] in '.!?:' and 
                    line and line[0].islower()):
                    current_sentence += " " + line
                else:
                    if current_sentence:
                        fixed_lines.append(current_sentence)
                    current_sentence = line
            
            if current_sentence:
                fixed_lines.append(current_sentence)
            
            if fixed_lines:
                fixed_paragraphs.append('\n'.join(fixed_lines))
        
        return '\n\n'.join(fixed_paragraphs)

    def remove_isolated_characters(self, text: str) -> str:
        """Remove isolated single characters that are likely OCR artifacts."""
        # Remove lines with only single characters or very short meaningless content
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip lines that are just single characters, numbers, or very short
            if (len(line) <= 2 and 
                not line.isdigit() and 
                line not in ['UK', 'EU', 'US', 'UN', 'MP', 'PM']):  # Keep important abbreviations
                continue
            # Skip lines with mostly special characters
            if len(line) > 0 and sum(c in string.punctuation for c in line) / len(line) > 0.7:
                continue
            # Skip lines that are just page numbers
            if re.match(r'^-?\s*\d{1,3}\s*-?$', line):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def fix_word_breaks(self, text: str) -> str:
        """Fix words broken with hyphens at line ends."""
        # Fix hyphenated words at line ends
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # But preserve intentional hyphenated words
        # This is a simple heuristic - could be improved
        text = re.sub(r'(\w+)-(\w+)', lambda m: m.group(0) if len(m.group(1)) > 2 and len(m.group(2)) > 2 else m.group(1) + m.group(2), text)
        
        return text

    def remove_excessive_whitespace_lines(self, text: str) -> str:
        """Remove lines that are mostly whitespace or dots."""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that are mostly dots, underscores, dashes, or spaces
            if re.match(r'^[\s._-]*$', line):
                continue
            # Skip lines with repetitive characters (like ...........)
            if len(line) > 5 and len(set(line.strip())) <= 2:
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def clean_text(self, text: str) -> str:
        """Apply all cleaning steps to the text."""
        print("  Normalizing unicode...")
        text = self.normalize_unicode(text)
        
        print("  Fixing OCR character errors...")
        text = self.fix_ocr_character_errors(text)
        
        print("  Removing noise patterns...")
        text = self.remove_noise_patterns(text)
        
        print("  Fixing fragmented text...")
        text = self.fix_fragmented_text(text)
        
        print("  Fixing punctuation spacing...")
        text = self.fix_punctuation_spacing(text)
        
        print("  Removing isolated characters...")
        text = self.remove_isolated_characters(text)
        
        print("  Fixing word breaks...")
        text = self.fix_word_breaks(text)
        
        print("  Removing excessive whitespace lines...")
        text = self.remove_excessive_whitespace_lines(text)
        
        print("  Removing header/footer repetition...")
        text = self.remove_header_footer_repetition(text)
        
        print("  Fixing broken sentences...")
        text = self.fix_broken_sentences(text)
        
        print("  Normalizing spacing...")
        text = self.normalize_spacing(text)
        
        # Final cleanup
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Normalize paragraph breaks
        text = text.strip()
        
        return text


def clean_manifesto_file(input_path: str, output_path: str = None) -> str:
    """Clean a single manifesto text file."""
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        return None
    
    # Generate output path if not provided
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_cleaned.txt"
    else:
        output_path = Path(output_path)
    
    print(f"Cleaning: {input_path.name}")
    
    # Read the input file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        # Try different encodings if UTF-8 fails
        try:
            with open(input_path, 'r', encoding='latin-1') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    # Clean the text
    cleaner = TextCleaner()
    cleaned_text = cleaner.clean_text(text)
    
    # Write the cleaned text
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        print(f"Cleaned text saved to: {output_path}")
        return str(output_path)
    except Exception as e:
        print(f"Error saving cleaned file: {e}")
        return None


def clean_manifesto_directory(input_dir: str, output_dir: str = None):
    """Clean all text files in a directory."""
    input_dir = Path(input_dir)
    
    if not input_dir.exists():
        print(f"Error: Directory not found: {input_dir}")
        return
    
    # Set output directory
    if output_dir is None:
        output_dir = input_dir / "cleaned"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all text files
    text_files = list(input_dir.glob("*.txt"))
    
    if not text_files:
        print(f"No .txt files found in: {input_dir}")
        return
    
    print(f"Found {len(text_files)} text files to clean")
    print(f"Output directory: {output_dir}")
    print("-" * 60)
    
    # Process each file
    for i, text_file in enumerate(text_files, 1):
        print(f"\n[{i}/{len(text_files)}]")
        output_path = output_dir / f"{text_file.stem}_cleaned.txt"
        clean_manifesto_file(str(text_file), str(output_path))
    
    print(f"\n{'='*60}")
    print("CLEANING COMPLETE")
    print(f"Cleaned files saved to: {output_dir}")

if __name__ == "__main__":
    # Configuration
    input_directory = "/Users/user/programming/manifestos_and_identity/2a_text_output_files"
    output_directory = "/Users/user/programming/manifestos_and_identity/2b_cleaned_text_files"
    
    # Clean all files in the directory
    clean_manifesto_directory(input_directory, output_directory)
    