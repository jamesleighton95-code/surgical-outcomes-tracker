import pymssql
import os
from contextlib import contextmanager
from typing import Dict, List, Optional

# Database connection parameters - should be stored in Azure Key Vault in production
DB_SERVER = os.environ.get('DB_SERVER', 'your-server.database.windows.net')
DB_NAME = os.environ.get('DB_NAME', 'surgical-outcomes-db')
DB_USER = os.environ.get('DB_USER', 'dbadmin')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your-password')

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = pymssql.connect(
        server=DB_SERVER,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# User queries
def create_user(email: str, password_hash: str, name: str, role: str = 'consultant', specialty: str = None) -> str:
    """Create a new user and return their ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Users (Email, PasswordHash, Name, Role, Specialty, CreatedAt)
            OUTPUT INSERTED.UserId
            VALUES (%s, %s, %s, %s, %s, GETDATE())
        """, (email, password_hash, name, role, specialty))
        result = cursor.fetchone()
        return str(result[0])

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email."""
    with get_db_connection() as conn:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("""
            SELECT UserId, Email, PasswordHash, Name, Role, Specialty, CreatedAt
            FROM Users
            WHERE Email = %s
        """, (email,))
        return cursor.fetchone()

def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("""
            SELECT UserId, Email, Name, Role, Specialty, CreatedAt
            FROM Users
            WHERE UserId = %s
        """, (user_id,))
        return cursor.fetchone()

# Case queries
def create_case(user_id: str, case_data: Dict) -> str:
    """Create a new theatre case."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Cases (
                UserId, ProcedureType, ProcedureName, DatePerformed,
                PatientAge, PatientSex, ASAGrade, DurationMinutes,
                Complications, Outcome, Notes, CreatedAt
            )
            OUTPUT INSERTED.CaseId
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, GETDATE())
        """, (
            user_id,
            case_data.get('procedureType'),
            case_data.get('procedureName'),
            case_data.get('datePerformed'),
            case_data.get('patientAge'),
            case_data.get('patientSex'),
            case_data.get('asaGrade'),
            case_data.get('durationMinutes'),
            case_data.get('complications'),
            case_data.get('outcome'),
            case_data.get('notes')
        ))
        result = cursor.fetchone()
        return str(result[0])

def get_cases_by_user(user_id: str, limit: int = 100, offset: int = 0) -> List[Dict]:
    """Get all cases for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("""
            SELECT * FROM Cases
            WHERE UserId = %s
            ORDER BY DatePerformed DESC
            OFFSET %s ROWS FETCH NEXT %s ROWS ONLY
        """, (user_id, offset, limit))
        return cursor.fetchall()

def get_case_by_id(case_id: str, user_id: str) -> Optional[Dict]:
    """Get a specific case by ID (ensuring it belongs to the user)."""
    with get_db_connection() as conn:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("""
            SELECT * FROM Cases
            WHERE CaseId = %s AND UserId = %s
        """, (case_id, user_id))
        return cursor.fetchone()

def update_case(case_id: str, user_id: str, case_data: Dict) -> bool:
    """Update an existing case."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Cases
            SET ProcedureType = %s, ProcedureName = %s, DatePerformed = %s,
                PatientAge = %s, PatientSex = %s, ASAGrade = %s, DurationMinutes = %s,
                Complications = %s, Outcome = %s, Notes = %s, UpdatedAt = GETDATE()
            WHERE CaseId = %s AND UserId = %s
        """, (
            case_data.get('procedureType'),
            case_data.get('procedureName'),
            case_data.get('datePerformed'),
            case_data.get('patientAge'),
            case_data.get('patientSex'),
            case_data.get('asaGrade'),
            case_data.get('durationMinutes'),
            case_data.get('complications'),
            case_data.get('outcome'),
            case_data.get('notes'),
            case_id,
            user_id
        ))
        return cursor.rowcount > 0

def delete_case(case_id: str, user_id: str) -> bool:
    """Delete a case."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM Cases
            WHERE CaseId = %s AND UserId = %s
        """, (case_id, user_id))
        return cursor.rowcount > 0

# Statistics queries
def get_case_statistics(user_id: str, filters: Dict = None) -> Dict:
    """Get statistics for a user's cases."""
    with get_db_connection() as conn:
        cursor = conn.cursor(as_dict=True)

        # Build WHERE clause based on filters
        where_clauses = ["UserId = %s"]
        params = [user_id]

        if filters:
            if filters.get('procedureType'):
                where_clauses.append("ProcedureType = %s")
                params.append(filters['procedureType'])
            if filters.get('startDate'):
                where_clauses.append("DatePerformed >= %s")
                params.append(filters['startDate'])
            if filters.get('endDate'):
                where_clauses.append("DatePerformed <= %s")
                params.append(filters['endDate'])

        where_clause = " AND ".join(where_clauses)

        cursor.execute(f"""
            SELECT
                COUNT(*) as TotalCases,
                COUNT(CASE WHEN Complications = 'none' OR Complications IS NULL THEN 1 END) as CasesWithoutComplications,
                AVG(CAST(DurationMinutes as FLOAT)) as AvgDuration,
                COUNT(CASE WHEN Outcome = 'positive' THEN 1 END) as PositiveOutcomes,
                COUNT(CASE WHEN Outcome = 'negative' THEN 1 END) as NegativeOutcomes
            FROM Cases
            WHERE {where_clause}
        """, tuple(params))

        return cursor.fetchone()

def search_cases(user_id: str, query: str) -> List[Dict]:
    """Search cases by procedure name or notes."""
    with get_db_connection() as conn:
        cursor = conn.cursor(as_dict=True)
        search_pattern = f'%{query}%'
        cursor.execute("""
            SELECT * FROM Cases
            WHERE UserId = %s AND (
                ProcedureName LIKE %s OR
                Notes LIKE %s OR
                ProcedureType LIKE %s
            )
            ORDER BY DatePerformed DESC
        """, (user_id, search_pattern, search_pattern, search_pattern))
        return cursor.fetchall()
