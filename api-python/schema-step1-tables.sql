-- Database schema for Surgical Outcomes Tracker - STEP 1: Tables Only
-- Azure SQL Database
-- Run this first, then run schema-step2-views.sql

-- Users table
CREATE TABLE Users (
    UserId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Email NVARCHAR(255) UNIQUE NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL,
    Name NVARCHAR(255) NOT NULL,
    Role NVARCHAR(50) NOT NULL DEFAULT 'consultant',
    Specialty NVARCHAR(100),
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2,
    INDEX idx_email (Email)
);

-- Cases table - stores theatre case information
CREATE TABLE Cases (
    CaseId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserId UNIQUEIDENTIFIER NOT NULL,
    ProcedureType NVARCHAR(100) NOT NULL,
    ProcedureName NVARCHAR(255) NOT NULL,
    DatePerformed DATE NOT NULL,
    PatientAge INT,
    PatientSex NVARCHAR(10),
    ASAGrade INT,
    DurationMinutes INT,
    Complications NVARCHAR(MAX),
    Outcome NVARCHAR(50),
    Notes NVARCHAR(MAX),
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2,
    FOREIGN KEY (UserId) REFERENCES Users(UserId) ON DELETE CASCADE,
    INDEX idx_user_date (UserId, DatePerformed),
    INDEX idx_procedure_type (ProcedureType),
    INDEX idx_date (DatePerformed)
);

-- Custom metrics table
CREATE TABLE CustomMetrics (
    MetricId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    CaseId UNIQUEIDENTIFIER NOT NULL,
    MetricName NVARCHAR(100) NOT NULL,
    MetricValue NVARCHAR(255) NOT NULL,
    MetricUnit NVARCHAR(50),
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (CaseId) REFERENCES Cases(CaseId) ON DELETE CASCADE,
    INDEX idx_case_metric (CaseId, MetricName)
);

-- Outcomes tracking
CREATE TABLE Outcomes (
    OutcomeId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    CaseId UNIQUEIDENTIFIER NOT NULL,
    OutcomeType NVARCHAR(100) NOT NULL,
    OutcomeValue NVARCHAR(255) NOT NULL,
    FollowUpDate DATE,
    Notes NVARCHAR(MAX),
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (CaseId) REFERENCES Cases(CaseId) ON DELETE CASCADE,
    INDEX idx_case_outcome (CaseId, OutcomeType)
);

-- Attachments table
CREATE TABLE Attachments (
    AttachmentId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    CaseId UNIQUEIDENTIFIER NOT NULL,
    FileName NVARCHAR(255) NOT NULL,
    FileUrl NVARCHAR(MAX) NOT NULL,
    FileType NVARCHAR(50),
    UploadedAt DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (CaseId) REFERENCES Cases(CaseId) ON DELETE CASCADE,
    INDEX idx_case_attachment (CaseId)
);

-- Saved queries table
CREATE TABLE SavedQueries (
    QueryId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserId UNIQUEIDENTIFIER NOT NULL,
    QueryName NVARCHAR(255) NOT NULL,
    QueryText NVARCHAR(MAX) NOT NULL,
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    LastUsed DATETIME2,
    FOREIGN KEY (UserId) REFERENCES Users(UserId) ON DELETE CASCADE,
    INDEX idx_user_query (UserId)
);

-- Audit log
CREATE TABLE AuditLog (
    LogId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserId UNIQUEIDENTIFIER NOT NULL,
    EntityType NVARCHAR(50) NOT NULL,
    EntityId UNIQUEIDENTIFIER NOT NULL,
    Action NVARCHAR(50) NOT NULL,
    Changes NVARCHAR(MAX),
    Timestamp DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (UserId) REFERENCES Users(UserId),
    INDEX idx_user_timestamp (UserId, Timestamp),
    INDEX idx_entity (EntityType, EntityId)
);
