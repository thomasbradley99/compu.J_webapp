import os
from typing import Optional
from PyPDF2 import PdfReader
from docx import Document
from app.core.config import settings

class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from a PDF file."""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from a DOCX file."""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()

    @staticmethod
    def read_text_file(file_path: str) -> str:
        """Read text from a plain text file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()

    @classmethod
    def process_document(cls, file_path: str) -> Optional[str]:
        """
        Process a document and extract its text content based on file type.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content or None if processing fails
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return cls.extract_text_from_pdf(file_path)
            elif file_extension == '.docx':
                return cls.extract_text_from_docx(file_path)
            elif file_extension == '.txt':
                return cls.read_text_file(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            print(f"Error processing document {file_path}: {str(e)}")
            return None

    @staticmethod
    def validate_file(file_path: str) -> bool:
        """
        Validate if the file is allowed and within size limits.
        
        Args:
            file_path: Path to the file
            
        Returns:
            bool indicating if the file is valid
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        return (
            file_extension in settings.ALLOWED_EXTENSIONS
            and file_size <= settings.MAX_FILE_SIZE
        ) 