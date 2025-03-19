# Smart Doc Classifier

A modern web application that automatically classifies documents using AI. Built with FastAPI, React, and PostgreSQL.

## ✨ Current Features

### 🚀 Core Functionality
- **Smart Upload System**
  - Drag-and-drop interface
  - Multi-file upload support
  - Supports TXT, PDF, and DOCX files
  - Real-time upload status feedback

- **AI-Powered Classification**
  - Uses BART model for zero-shot classification
  - 6 document categories (Technical, Business, Legal, Academic, General, Other)
  - Confidence scoring for each classification
  - Batch processing capability

- **Interactive Dashboard**
  - Total document count
  - Category distribution visualization
  - Most common document types
  - Average documents per category
  - Auto-refreshing stats (30-second intervals)

- **Document History**
  - Complete upload history
  - Classification results
  - Confidence scores
  - Upload timestamps

### 💻 Technical Features
- FastAPI backend with SQLAlchemy ORM
- React frontend with Tailwind CSS
- PostgreSQL database
- Real-time error handling
- Responsive design

## 🔄 Auto-Updating Statistics
- Live document count
- Category distribution
- Confidence level indicators
- Processing status updates

## Project Overview

A1 Smart Doc Classifier is designed to help users automatically categorize their documents using advanced machine learning techniques. The application provides a simple, intuitive interface for document upload and classification, making it easy to organize and manage documents based on their content.

### Core Features

- **Document Upload**: Support for text files with drag-and-drop interface
- **Automatic Classification**: Uses Hugging Face's BART model for zero-shot classification
- **Document Categories**:
  - Technical Documentation
  - Business Proposal
  - Legal Document
  - Academic Paper
  - General Article
  - Other
- **Classification Results**: Shows predicted category and confidence scores
- **Document History**: View and manage previously classified documents

### Technical Stack

#### Backend
- Node.js + Express
- PostgreSQL Database
- Hugging Face Transformers for ML
- JWT for authentication
- Multer for file handling

#### Frontend
- React.js
- Tailwind CSS for styling
- Axios for API calls
- React Router for navigation

## Project Structure

```
A1_smart_doc_classifier/
├── backend/
│   ├── src/
│   │   ├── config/          # Database and environment configurations
│   │   ├── controllers/     # Route handlers
│   │   ├── models/         # Database models
│   │   ├── routes/         # API routes
│   │   ├── services/       # Business logic and ML integration
│   │   └── utils/          # Helper functions
│   ├── .env                # Environment variables
│   └── package.json
└── frontend/
    ├── src/
    │   ├── components/     # Reusable React components
    │   │   ├── DocumentUpload/
    │   │   ├── ClassificationResult/
    │   │   └── DocumentList/
    │   ├── services/       # API integration
    │   └── App.js
    └── package.json
```

## Database Schema

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    predicted_category VARCHAR(50) NOT NULL,
    confidence_score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Document Management
- `POST /api/documents/upload`
  - Upload and classify a document
  - Returns classification result

- `GET /api/documents`
  - List all classified documents
  - Supports pagination

## Environment Variables

```env
# Database
DB_USER=postgres
DB_HOST=clann-db-11nov.cfcgo2cma4or.eu-west-1.rds.amazonaws.com
DB_NAME=postgres
DB_PASSWORD=ClannPass123!
DB_PORT=5432

# Server Config
PORT=3001
JWT_SECRET=doc_classifier_secret_key_2024

# ML Model
ML_MODEL_NAME=facebook/bart-large-mnli

# Client URL
CLIENT_URL=http://localhost:3002
```

## Development Roadmap

### Phase 1: MVP
- [x] Basic project structure
- [ ] Database setup
- [ ] Backend API implementation
- [ ] Frontend components
- [ ] ML model integration
- [ ] Basic document upload and classification

### Phase 2: Enhancement
- [ ] User authentication
- [ ] Enhanced UI/UX
- [ ] Support for more file types (PDF, DOCX)
- [ ] Document preview
- [ ] Batch processing
- [ ] Statistics dashboard

### Phase 3: Optimization
- [ ] Performance optimization
- [ ] Caching implementation
- [ ] Error handling improvements
- [ ] Testing suite
- [ ] Documentation

## Getting Started

1. Clone the repository
2. Set up environment variables
3. Install dependencies:
   ```bash
   # Backend
   cd backend
   npm install

   # Frontend
   cd ../frontend
   npm install
   ```
4. Start the development servers:
   ```bash
   # Backend
   cd backend
   npm run dev

   # Frontend
   cd frontend
   npm run dev
   ```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT License 