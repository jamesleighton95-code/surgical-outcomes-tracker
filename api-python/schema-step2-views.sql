-- Database schema for Surgical Outcomes Tracker - STEP 2: Views
-- Azure SQL Database
-- Run this AFTER schema-step1-tables.sql

-- Create a view for case statistics
GO
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

GO
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
