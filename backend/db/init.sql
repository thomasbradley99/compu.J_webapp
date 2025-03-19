DROP DATABASE IF EXISTS doc_classifier;
CREATE DATABASE doc_classifier;
\c doc_classifier

DROP TABLE IF EXISTS documents;
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    predicted_category VARCHAR(100) NOT NULL,
    confidence_score FLOAT NOT NULL,
    category_scores JSONB NOT NULL,
    token_count INTEGER,
    num_chunks INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    title VARCHAR(255),
    description TEXT,
    tags JSONB
); 