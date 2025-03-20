# Smart Doc Classifier

A modern web application that automatically classifies documents using AI. Built with FastAPI, React, and PostgreSQL.

## 🎯 Project Overview

Smart Doc Classifier uses zero-shot classification to automatically categorize documents into predefined categories. It uses the BART-large-MNLI model for intelligent classification while incorporating feature-based adjustments for improved accuracy.

### Important Note
On first run, the application will automatically download the BART-large-MNLI model (approximately 1.6GB). This is a one-time download and no authentication token is required.

### Why BART-large-MNLI?
- **Zero-shot Capabilities**: No training data required
- **Robust Performance**: Strong accuracy across diverse document types
- **Feature Integration**: Easily combines with custom rule-based enhancements
- **Production Ready**: Stable and well-maintained by Hugging Face

### Classification Categories
- Technical Documentation
- Business Proposal
- Legal Document
- Academic Paper
- General Article
- Other

## ✨ Key Features

### 🚀 Document Processing
- Drag-and-drop file upload interface
- Support for TXT, PDF, and DOCX files
- Intelligent text extraction
- Automatic chunking for long documents
- Batch processing capability

### 🤖 ML Pipeline
- Zero-shot classification using BART
- Feature-based score adjustments
- Confidence scoring with three levels:
  - High (>50%): Strong classification confidence
  - Medium (30-50%): Reasonable confidence
  - Low (<30%): Manual review recommended
- Document structure analysis
- Title and content-based feature extraction

### 📊 Analytics Dashboard
- Real-time document statistics
- Category distribution visualization
- Confidence score tracking
- Processing status updates
- Auto-refreshing (30s intervals)

## 💻 Technical Stack

### Backend
- FastAPI for API endpoints
- PostgreSQL with SQLAlchemy ORM
- Pydantic for data validation
- Hugging Face Transformers
- PyPDF2 & python-docx for file processing

### Frontend
- React with Hooks
- Tailwind CSS for styling
- Axios for API communication
- Real-time error handling
- Responsive design

## 🛠️ Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/thomasbradley99/compu.J_webapp.git
   cd compu.J_webapp
   ```

2. **Install Dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   ```

3. **Database Setup**
   ```bash
   # Create PostgreSQL database (from project root)
   psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'doc_classifier' AND pid <> pg_backend_pid();"
   psql -U postgres -f backend/db/init.sql
   ```

4. **Start the Application**
   ```bash
   # Start backend (from backend directory)
   uvicorn app.main:app --reload --port 8000

   # Start frontend (from frontend directory)
   npm start
   ```

Note: The application uses default PostgreSQL configuration:
- Server: localhost
- User: postgres
- Database: doc_classifier
- Port: 5432

If you need to modify these settings, they can be found in `backend/app/core/config.py`.

## 🔄 Error Handling

The application implements comprehensive error handling:

### Document Processing
- File type validation
- Size limit checks (10MB max)
- Corrupt file detection
- Text extraction fallbacks

### ML Pipeline
- Token limit handling through chunking
- Low confidence warnings
- Feature extraction error recovery
- Model fallback options

### API Layer
- Request validation
- Database transaction protection
- Detailed error responses
- Rate limiting

## 📈 Future Improvements

1. **ML Pipeline**
   - Implement alternative models for comparison
   - Add confidence threshold customization
   - Enhance feature extraction

2. **User Interface**
   - Add document history sorting/filtering
   - Implement pagination
   - Add detailed document preview

3. **Infrastructure**
   - Add caching layer
   - Implement user authentication
   - Add API documentation
   - Expand test coverage

## 📝 License

MIT License - see LICENSE file for details 