from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from datetime import datetime

from app.core.config import settings
from app.db.session import get_db
from app.models.document import Document
from app.services.classifier import DocumentClassifier
from app.services.document_processor import DocumentProcessor

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize classifier
classifier = DocumentClassifier()

@app.post("/api/classify")
async def classify_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Validate file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Save uploaded file
        file_path = f"uploads/{uuid.uuid4()}{file_extension}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Process document using the appropriate method
        text_content = DocumentProcessor.process_document(file_path)
        if not text_content:
            raise HTTPException(status_code=400, detail="Failed to process document")

        # Classify document
        result = classifier.classify_document(text_content)

        # Save to database
        document = Document(
            filename=os.path.basename(file_path),
            original_filename=file.filename,
            file_path=file_path,
            file_type=file_extension,
            file_size=len(content),
            predicted_category=result["predicted_category"],
            confidence_score=result["confidence_score"],
            category_scores=result["category_scores"]
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        return result

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/classify-batch")
async def classify_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    results = []
    for file in files:
        try:
            # Create uploads directory if it doesn't exist
            os.makedirs("uploads", exist_ok=True)
            
            # Validate file extension
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in settings.ALLOWED_EXTENSIONS:
                results.append({
                    "filename": file.filename,
                    "error": f"Unsupported file type. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
                })
                continue
            
            # Process file and get classification
            file_path = f"uploads/{uuid.uuid4()}{file_extension}"
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            text_content = DocumentProcessor.process_document(file_path)
            if not text_content:
                results.append({
                    "filename": file.filename,
                    "error": "Failed to process document"
                })
                continue

            result = classifier.classify_document(text_content)
            
            # Save to database
            document = Document(
                filename=os.path.basename(file_path),
                original_filename=file.filename,
                file_path=file_path,
                file_type=file_extension,
                file_size=len(content),
                predicted_category=result["predicted_category"],
                confidence_score=result["confidence_score"],
                category_scores=result["category_scores"]
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            
            results.append({
                "filename": file.filename,
                **result
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })

    return results

@app.get("/api/documents")
def get_documents(db: Session = Depends(get_db)):
    """Get all classified documents"""
    documents = db.query(Document).order_by(Document.created_at.desc()).all()
    return documents

@app.get(f"{settings.API_V1_STR}/documents")
def list_documents(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    List all classified documents with pagination.
    """
    documents = db.query(Document).offset(skip).limit(limit).all()
    return documents

@app.get(f"{settings.API_V1_STR}/documents/{{document_id}}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific document.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    return document

@app.get(f"{settings.API_V1_STR}/documents/stats")
def get_document_stats(db: Session = Depends(get_db)):
    """
    Get statistics about classified documents.
    """
    total_documents = db.query(Document).count()
    category_counts = db.query(
        Document.predicted_category,
        func.count(Document.id)
    ).group_by(Document.predicted_category).all()
    
    return {
        "total_documents": total_documents,
        "category_distribution": dict(category_counts)
    } 