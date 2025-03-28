from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from datetime import datetime, timezone
from sqlalchemy import func

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
        # Validate file size
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "File too large",
                    "max_size": f"{settings.MAX_FILE_SIZE/1024/1024}MB",
                    "received_size": f"{len(content)/1024/1024}MB"
                }
            )
            
        # Enhanced file validation
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail={
                    "error": "Unsupported file type",
                    "allowed_types": settings.ALLOWED_EXTENSIONS,
                    "received_type": file_extension
                }
            )
            
        # Process document with enhanced error handling
        try:
            text_content = DocumentProcessor.process_document(file_path)
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=422,
                detail="File encoding not supported. Please ensure the file is properly encoded (UTF-8 recommended)."
            )
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Failed to process document: {str(e)}"
            )

        # Validate file content
        if not text_content or len(text_content.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid document content",
                    "reason": "Document appears to be empty or corrupted"
                }
            )

        # Extract text from the document
        text = await process_document_content(content, file.filename)
        
        # Get classification results
        result = classifier.classify_document(text, file.filename)

        # Save to database
        document = Document(
            filename=os.path.basename(file_path),
            original_filename=file.filename,
            file_path=file_path,
            file_type=file_extension,
            file_size=len(content),
            predicted_category=result["predicted_category"],
            confidence_score=result["confidence_score"],
            category_scores=result["category_scores"],
            token_count=result.get("token_count"),
            num_chunks=result.get("num_chunks")
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

            result = classifier.classify_document(text_content, file.filename)
            
            # Save to database
            document = Document(
                filename=os.path.basename(file_path),
                original_filename=file.filename,
                file_path=file_path,
                file_type=file_extension,
                file_size=len(content),
                predicted_category=result["predicted_category"],
                confidence_score=result["confidence_score"],
                category_scores=result["category_scores"],
                token_count=result.get("token_count"),
                num_chunks=result.get("num_chunks")
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

@app.get("/api/stats")
async def get_document_stats(db: Session = Depends(get_db)):
    try:
        # Get total documents
        total_documents = db.query(Document).count()
        
        # Get category distribution and additional stats
        documents = db.query(Document).all()
        
        # Calculate category distribution
        category_distribution = {}
        for doc in documents:
            category_distribution[doc.predicted_category] = category_distribution.get(doc.predicted_category, 0) + 1
        
        return {
            "total_documents": total_documents,
            "category_distribution": category_distribution,
            "documents": [
                {
                    "confidence_score": doc.confidence_score,
                    "file_size": doc.file_size,
                    "token_count": doc.token_count,
                    "num_chunks": doc.num_chunks
                } for doc in documents
            ]
        }
        
    except Exception as e:
        print(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch document statistics") 