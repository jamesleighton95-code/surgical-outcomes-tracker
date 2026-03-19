-- Database schema for Surgical Outcomes Tracker
-- Azure SQL Database

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
    ProcedureType NVARCHAR(100) NOT NULL, -- e.g., 'Laparoscopic', 'Open', 'Endoscopic'
    ProcedureName NVARCHAR(255) NOT NULL, -- e.g., 'Laparoscopic Cholecystectomy'
    DatePerformed DATE NOT NULL,
    PatientAge INT,
    PatientSex NVARCHAR(10), -- 'M', 'F', 'Other'
    ASAGrade INT, -- ASA physical status classification (1-5)
    DurationMinutes INT, -- Procedure duration
    Complications NVARCHAR(MAX), -- JSON or comma-separated list
    Outcome NVARCHAR(50), -- 'positive', 'negative', 'neutral'
    Notes NVARCHAR(MAX), -- Additional notes, no patient identifiable info
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    UpdatedAt DATETIME2,
    FOREIGN KEY (UserId) REFERENCES Users(UserId) ON DELETE CASCADE,
    INDEX idx_user_date (UserId, DatePerformed),
    INDEX idx_procedure_type (ProcedureType),
    INDEX idx_date (DatePerformed)
);

-- Custom metrics table - for tracking specific outcomes
CREATE TABLE CustomMetrics (
    MetricId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    CaseId UNIQUEIDENTIFIER NOT NULL,
    MetricName NVARCHAR(100) NOT NULL, -- e.g., 'Margin Status', 'Blood Loss', 'Lymph Node Count'
    MetricValue NVARCHAR(255) NOT NULL,
    MetricUnit NVARCHAR(50), -- e.g., 'ml', 'cm', 'count'
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (CaseId) REFERENCES Cases(CaseId) ON DELETE CASCADE,
    INDEX idx_case_metric (CaseId, MetricName)
);

-- Outcomes tracking - for detailed outcome data
CREATE TABLE Outcomes (
    OutcomeId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    CaseId UNIQUEIDENTIFIER NOT NULL,
    OutcomeType NVARCHAR(100) NOT NULL, -- e.g., 'Margin Status', 'Conversion Rate', 'Readmission'
    OutcomeValue NVARCHAR(255) NOT NULL,
    FollowUpDate DATE, -- When the outcome was assessed
    Notes NVARCHAR(MAX),
    CreatedAt DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (CaseId) REFERENCES Cases(CaseId) ON DELETE CASCADE,
    INDEX idx_case_outcome (CaseId, OutcomeType)
);

-- Attachments table - for storing file references
CREATE TABLE Attachments (
    AttachmentId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    CaseId UNIQUEIDENTIFIER NOT NULL,
    FileName NVARCHAR(255) NOT NULL,
    FileUrl NVARCHAR(MAX) NOT NULL, -- Azure Blob Storage URL
    FileType NVARCHAR(50), -- 'image', 'pdf', 'document'
    UploadedAt DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (CaseId) REFERENCES Cases(CaseId) ON DELETE CASCADE,
    INDEX idx_case_attachment (CaseId)
);

-- Saved queries table - for storing frequently used queries
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

-- Audit log for tracking changes (optional but recommended)
CREATE TABLE AuditLog (
    LogId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    UserId UNIQUEIDENTIFIER NOT NULL,
    EntityType NVARCHAR(50) NOT NULL, -- 'Case', 'User', etc.
    EntityId UNIQUEIDENTIFIER NOT NULL,
    Action NVARCHAR(50) NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE'
    Changes NVARCHAR(MAX), -- JSON of what changed
    Timestamp DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (UserId) REFERENCES Users(UserId),
    INDEX idx_user_timestamp (UserId, Timestamp),
    INDEX idx_entity (EntityType, EntityId)
);

-- Create a view for case statistics
CREATE VIEW vw_CaseStatistics AS
SELECT
    u.UserId,
    u.Name as ConsultantName,
    u.Specialty,
    COUNT(c.CaseId) as TotalCases,
    COUNT(DISTINCT c.ProcedureType) as UniqueProcedureTypes,
    MIN(c.DatePerformed) as FirstCaseDate,
    MAX(c.DatePerformed) as LastCaseDate,
    AVG(CAST(c.DurationMinutes as FLOAT)) as AvgDuration,
    COUNT(CASE WHEN c.Outcome = 'positive' THEN 1 END) as PositiveOutcomes,
    COUNT(CASE WHEN c.Outcome = 'negative' THEN 1 END) as NegativeOutcomes,
    COUNT(CASE WHEN c.Complications IS NULL OR c.Complications = 'none' THEN 1 END) as CasesWithoutComplications
FROM Users u
LEFT JOIN Cases c ON u.UserId = c.UserId
GROUP BY u.UserId, u.Name, u.Specialty;

-- Create a view for recent cases
CREATE VIEW vw_RecentCases AS
SELECT TOP 100
    c.CaseId,
    c.UserId,
    u.Name as ConsultantName,
    c.ProcedureType,
    c.ProcedureName,
    c.DatePerformed,
    c.DurationMinutes,
    c.Outcome,
    c.CreatedAt
FROM Cases c
INNER JOIN Users u ON c.UserId = u.UserId
ORDER BY c.DatePerformed DESC;

-- Sample data for development (optional)
-- Uncomment the following lines if you want sample data

/*
-- Insert a test user
INSERT INTO Users (Email, PasswordHash, Name, Role, Specialty)
VALUES ('test@example.com', '$2b$10$samplehashhere', 'Dr. Test Consultant', 'consultant', 'General Surgery');

-- Get the UserId of the test user
DECLARE @TestUserId UNIQUEIDENTIFIER = (SELECT UserId FROM Users WHERE Email = 'test@example.com');

-- Insert sample cases
INSERT INTO Cases (UserId, ProcedureType, ProcedureName, DatePerformed, PatientAge, PatientSex, ASAGrade, DurationMinutes, Complications, Outcome, Notes)
VALUES
    (@TestUserId, 'Laparoscopic', 'Laparoscopic Cholecystectomy', '2024-01-15', 45, 'F', 2, 65, 'none', 'positive', 'Routine case, no complications'),
    (@TestUserId, 'Open', 'Right Hemicolectomy', '2024-01-20', 68, 'M', 3, 180, 'minor bleeding', 'positive', 'Good outcome despite minor bleeding'),
    (@TestUserId, 'Laparoscopic', 'Inguinal Hernia Repair', '2024-01-25', 55, 'M', 2, 90, 'none', 'positive', 'Straightforward repair');
*/
