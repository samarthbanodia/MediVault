-- MediVault Supabase Database Schema
-- Copy-paste this into Supabase SQL Editor to create all tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE 1: users
-- Stores both patients and doctors
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- Null for OAuth users
    full_name VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('patient', 'doctor')),
    date_of_birth DATE,
    age INTEGER,
    gender VARCHAR(20),
    phone VARCHAR(20),
    address TEXT,

    -- Doctor-specific fields
    license_number VARCHAR(100) UNIQUE,
    specialization VARCHAR(100),
    hospital_affiliation VARCHAR(255),

    -- Auth metadata
    google_id VARCHAR(255) UNIQUE,
    profile_picture_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_type ON users(user_type);
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ============================================================================
-- TABLE 2: medical_records
-- Stores uploaded files and metadata
-- ============================================================================
CREATE TABLE medical_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id VARCHAR(100) UNIQUE NOT NULL, -- e.g., REC_20240115_123456
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- File information
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- pdf, jpg, png, etc.
    file_size INTEGER, -- bytes

    -- Document metadata
    document_type VARCHAR(100), -- prescription, lab_report, discharge_summary, etc.
    document_date DATE,
    issuing_hospital VARCHAR(255),
    issuing_doctor VARCHAR(255),

    -- Processing metadata
    ocr_text TEXT,
    ocr_confidence FLOAT,
    processing_status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed

    -- Clinical summary (OpenAI generated)
    clinical_summary TEXT,

    -- Severity and anomalies
    overall_severity INTEGER DEFAULT 0, -- 0-100
    has_critical_alerts BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for medical_records table
CREATE INDEX idx_medical_records_patient_id ON medical_records(patient_id);
CREATE INDEX idx_medical_records_record_id ON medical_records(record_id);
CREATE INDEX idx_medical_records_document_date ON medical_records(document_date);
CREATE INDEX idx_medical_records_severity ON medical_records(overall_severity);
CREATE INDEX idx_medical_records_created_at ON medical_records(created_at DESC);
CREATE INDEX idx_medical_records_status ON medical_records(processing_status);

-- ============================================================================
-- TABLE 3: biomarkers
-- Stores extracted health data from medical records
-- ============================================================================
CREATE TABLE biomarkers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id UUID NOT NULL REFERENCES medical_records(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Biomarker information
    biomarker_type VARCHAR(100) NOT NULL, -- glucose, bp_systolic, cholesterol, etc.
    value FLOAT NOT NULL,
    unit VARCHAR(50) NOT NULL, -- mg/dL, mmHg, etc.

    -- Reference ranges
    normal_min FLOAT,
    normal_max FLOAT,
    is_abnormal BOOLEAN DEFAULT FALSE,

    -- Context
    measurement_date DATE,
    extracted_text TEXT, -- Original text from OCR
    confidence FLOAT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for biomarkers table
CREATE INDEX idx_biomarkers_record_id ON biomarkers(record_id);
CREATE INDEX idx_biomarkers_patient_id ON biomarkers(patient_id);
CREATE INDEX idx_biomarkers_type ON biomarkers(biomarker_type);
CREATE INDEX idx_biomarkers_date ON biomarkers(measurement_date DESC);
CREATE INDEX idx_biomarkers_abnormal ON biomarkers(is_abnormal);
CREATE INDEX idx_biomarkers_patient_type ON biomarkers(patient_id, biomarker_type);

-- ============================================================================
-- TABLE 4: anomalies
-- Stores alerts and severity scores from 7-layer detection
-- ============================================================================
CREATE TABLE anomalies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id UUID NOT NULL REFERENCES medical_records(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Anomaly information
    anomaly_type VARCHAR(100) NOT NULL, -- range_check, critical_value, trend_analysis, etc.
    layer VARCHAR(50) NOT NULL, -- layer 1-7
    severity INTEGER NOT NULL CHECK (severity >= 0 AND severity <= 100),
    is_critical BOOLEAN DEFAULT FALSE,

    -- Details
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    recommendation TEXT,
    affected_biomarker VARCHAR(100),

    -- Metadata
    detection_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for anomalies table
CREATE INDEX idx_anomalies_record_id ON anomalies(record_id);
CREATE INDEX idx_anomalies_patient_id ON anomalies(patient_id);
CREATE INDEX idx_anomalies_severity ON anomalies(severity DESC);
CREATE INDEX idx_anomalies_critical ON anomalies(is_critical);
CREATE INDEX idx_anomalies_acknowledged ON anomalies(acknowledged);
CREATE INDEX idx_anomalies_date ON anomalies(detection_date DESC);

-- ============================================================================
-- TABLE 5: embeddings
-- Stores vector embeddings for semantic search
-- ============================================================================
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id UUID NOT NULL REFERENCES medical_records(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Embedding data
    embedding_vector FLOAT8[], -- Array of floats for semantic search
    embedding_model VARCHAR(100) DEFAULT 'paraphrase-multilingual-mpnet-base-v2',
    vector_dimension INTEGER DEFAULT 768,

    -- Content that was embedded
    embedded_text TEXT NOT NULL,
    chunk_index INTEGER DEFAULT 0, -- For large documents split into chunks
    total_chunks INTEGER DEFAULT 1,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for embeddings table
CREATE INDEX idx_embeddings_record_id ON embeddings(record_id);
CREATE INDEX idx_embeddings_patient_id ON embeddings(patient_id);
CREATE INDEX idx_embeddings_model ON embeddings(embedding_model);

-- Note: For production vector search, consider using pgvector extension:
-- CREATE EXTENSION IF NOT EXISTS vector;
-- ALTER TABLE embeddings ADD COLUMN embedding vector(768);
-- CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops);

-- ============================================================================
-- TABLE 6: doctor_access
-- Manages sharing and permissions between patients and doctors
-- ============================================================================
CREATE TABLE doctor_access (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Access control
    access_level VARCHAR(50) NOT NULL DEFAULT 'read', -- read, write, admin
    access_type VARCHAR(50) NOT NULL DEFAULT 'permanent', -- permanent, temporary, one_time

    -- Sharing metadata
    shared_by UUID REFERENCES users(id), -- Who granted the access
    share_link VARCHAR(255) UNIQUE, -- Unique link for sharing
    share_link_expires_at TIMESTAMP WITH TIME ZONE,

    -- Permissions
    can_view_records BOOLEAN DEFAULT TRUE,
    can_add_notes BOOLEAN DEFAULT TRUE,
    can_download BOOLEAN DEFAULT FALSE,
    can_share BOOLEAN DEFAULT FALSE,

    -- Access window
    valid_from TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_by UUID REFERENCES users(id),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE,

    -- Ensure unique patient-doctor pairs
    CONSTRAINT unique_patient_doctor UNIQUE (patient_id, doctor_id)
);

-- Indexes for doctor_access table
CREATE INDEX idx_doctor_access_patient_id ON doctor_access(patient_id);
CREATE INDEX idx_doctor_access_doctor_id ON doctor_access(doctor_id);
CREATE INDEX idx_doctor_access_share_link ON doctor_access(share_link);
CREATE INDEX idx_doctor_access_active ON doctor_access(is_active);
CREATE INDEX idx_doctor_access_expires ON doctor_access(share_link_expires_at);

-- ============================================================================
-- ADDITIONAL TABLES
-- ============================================================================

-- Table 7: Medications (extracted from prescriptions)
CREATE TABLE medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id UUID NOT NULL REFERENCES medical_records(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Medication information
    medication_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(100), -- e.g., "1+0+1" (morning, afternoon, evening)
    duration VARCHAR(100), -- e.g., "30 days"
    route VARCHAR(50), -- oral, injection, etc.

    -- Prescription metadata
    prescribed_by VARCHAR(255),
    prescribed_date DATE,
    start_date DATE,
    end_date DATE,

    -- Extraction metadata
    extracted_text TEXT,
    confidence FLOAT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_medications_record_id ON medications(record_id);
CREATE INDEX idx_medications_patient_id ON medications(patient_id);
CREATE INDEX idx_medications_name ON medications(medication_name);
CREATE INDEX idx_medications_date ON medications(prescribed_date DESC);

-- Table 8: Diseases/Conditions
CREATE TABLE diseases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    record_id UUID NOT NULL REFERENCES medical_records(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Disease information
    disease_name VARCHAR(255) NOT NULL,
    icd_code VARCHAR(20), -- ICD-10 code
    status VARCHAR(50) DEFAULT 'active', -- active, resolved, chronic

    -- Clinical details
    diagnosed_date DATE,
    diagnosed_by VARCHAR(255),
    severity VARCHAR(50), -- mild, moderate, severe

    -- Extraction metadata
    extracted_text TEXT,
    confidence FLOAT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_diseases_record_id ON diseases(record_id);
CREATE INDEX idx_diseases_patient_id ON diseases(patient_id);
CREATE INDEX idx_diseases_name ON diseases(disease_name);
CREATE INDEX idx_diseases_status ON diseases(status);

-- Table 9: Doctor Notes
CREATE TABLE doctor_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doctor_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    record_id UUID REFERENCES medical_records(id) ON DELETE SET NULL,

    -- Note content
    note_text TEXT NOT NULL,
    note_type VARCHAR(50) DEFAULT 'general', -- general, follow_up, prescription, etc.

    -- Metadata
    visit_date DATE,
    is_private BOOLEAN DEFAULT FALSE, -- Hidden from patient if true

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_doctor_notes_patient_id ON doctor_notes(patient_id);
CREATE INDEX idx_doctor_notes_doctor_id ON doctor_notes(doctor_id);
CREATE INDEX idx_doctor_notes_record_id ON doctor_notes(record_id);
CREATE INDEX idx_doctor_notes_date ON doctor_notes(visit_date DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE biomarkers ENABLE ROW LEVEL SECURITY;
ALTER TABLE anomalies ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctor_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE medications ENABLE ROW LEVEL SECURITY;
ALTER TABLE diseases ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctor_notes ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Patients can view their own medical records
CREATE POLICY "Patients can view own records" ON medical_records
    FOR SELECT USING (
        auth.uid() = patient_id OR
        EXISTS (
            SELECT 1 FROM doctor_access
            WHERE doctor_access.doctor_id = auth.uid()
            AND doctor_access.patient_id = medical_records.patient_id
            AND doctor_access.is_active = TRUE
        )
    );

-- Patients can insert their own records
CREATE POLICY "Patients can insert own records" ON medical_records
    FOR INSERT WITH CHECK (auth.uid() = patient_id);

-- Similar policies for biomarkers, anomalies, medications, diseases
CREATE POLICY "View own biomarkers" ON biomarkers
    FOR SELECT USING (
        auth.uid() = patient_id OR
        EXISTS (
            SELECT 1 FROM doctor_access
            WHERE doctor_access.doctor_id = auth.uid()
            AND doctor_access.patient_id = biomarkers.patient_id
            AND doctor_access.is_active = TRUE
        )
    );

CREATE POLICY "View own anomalies" ON anomalies
    FOR SELECT USING (
        auth.uid() = patient_id OR
        EXISTS (
            SELECT 1 FROM doctor_access
            WHERE doctor_access.doctor_id = auth.uid()
            AND doctor_access.patient_id = anomalies.patient_id
            AND doctor_access.is_active = TRUE
        )
    );

-- Doctors can view their authorized patients
CREATE POLICY "Doctors can view authorized access" ON doctor_access
    FOR SELECT USING (
        auth.uid() = patient_id OR auth.uid() = doctor_id
    );

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for medical_records table
CREATE TRIGGER update_medical_records_updated_at BEFORE UPDATE ON medical_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for diseases table
CREATE TRIGGER update_diseases_updated_at BEFORE UPDATE ON diseases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for doctor_notes table
CREATE TRIGGER update_doctor_notes_updated_at BEFORE UPDATE ON doctor_notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to check doctor access
CREATE OR REPLACE FUNCTION check_doctor_access(
    p_doctor_id UUID,
    p_patient_id UUID
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM doctor_access
        WHERE doctor_id = p_doctor_id
        AND patient_id = p_patient_id
        AND is_active = TRUE
        AND (valid_until IS NULL OR valid_until > NOW())
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Patient summary
CREATE OR REPLACE VIEW patient_summary AS
SELECT
    u.id as patient_id,
    u.full_name,
    u.age,
    COUNT(DISTINCT mr.id) as total_records,
    COUNT(DISTINCT CASE WHEN mr.has_critical_alerts THEN mr.id END) as critical_records,
    MAX(mr.created_at) as last_upload_date,
    AVG(mr.overall_severity) as avg_severity
FROM users u
LEFT JOIN medical_records mr ON u.id = mr.patient_id
WHERE u.user_type = 'patient'
GROUP BY u.id, u.full_name, u.age;

-- View: Recent anomalies
CREATE OR REPLACE VIEW recent_critical_anomalies AS
SELECT
    a.*,
    u.full_name as patient_name,
    mr.record_id,
    mr.document_date
FROM anomalies a
JOIN users u ON a.patient_id = u.id
JOIN medical_records mr ON a.record_id = mr.id
WHERE a.is_critical = TRUE
AND a.acknowledged = FALSE
ORDER BY a.detection_date DESC;

-- ============================================================================
-- INITIAL DATA / SEED DATA (Optional)
-- ============================================================================

-- Insert a test patient (for development)
-- Uncomment for testing:
-- INSERT INTO users (email, full_name, user_type, age, gender)
-- VALUES ('test.patient@example.com', 'Test Patient', 'patient', 35, 'male');

-- Insert a test doctor (for development)
-- INSERT INTO users (email, full_name, user_type, license_number, specialization)
-- VALUES ('test.doctor@example.com', 'Dr. Test', 'doctor', 'DOC12345', 'General Medicine');

-- ============================================================================
-- PERFORMANCE OPTIMIZATION QUERIES
-- ============================================================================

-- Create composite indexes for common query patterns
CREATE INDEX idx_medical_records_patient_date ON medical_records(patient_id, document_date DESC);
CREATE INDEX idx_biomarkers_patient_type_date ON biomarkers(patient_id, biomarker_type, measurement_date DESC);
CREATE INDEX idx_anomalies_patient_critical ON anomalies(patient_id, is_critical, detection_date DESC);

-- ============================================================================
-- DATABASE MAINTENANCE
-- ============================================================================

-- Analyze tables for query optimization
ANALYZE users;
ANALYZE medical_records;
ANALYZE biomarkers;
ANALYZE anomalies;
ANALYZE embeddings;
ANALYZE doctor_access;
ANALYZE medications;
ANALYZE diseases;
ANALYZE doctor_notes;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ MediVault database schema created successfully!';
    RAISE NOTICE '📊 Created 9 tables with indexes and constraints';
    RAISE NOTICE '🔒 Row Level Security enabled';
    RAISE NOTICE '⚡ Performance indexes created';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Review and test the schema';
    RAISE NOTICE '2. Configure Supabase authentication';
    RAISE NOTICE '3. Set up storage buckets for file uploads';
    RAISE NOTICE '4. Create backend API endpoints';
END $$;
