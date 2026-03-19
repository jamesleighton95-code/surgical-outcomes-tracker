import azure.functions as func
import json
import logging
from shared.auth import hash_password, verify_password, generate_token, require_auth
from shared.database import (
    create_user, get_user_by_email, get_user_by_id,
    create_case, get_cases_by_user, get_case_by_id, update_case, delete_case,
    get_case_statistics, search_cases
)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route(route="auth/register", methods=["POST"])
def register(req: func.HttpRequest) -> func.HttpResponse:
    """Register a new user."""
    try:
        body = req.get_json()
        email = body.get('email')
        password = body.get('password')
        name = body.get('name')
        specialty = body.get('specialty')

        if not email or not password or not name:
            return func.HttpResponse(
                '{"error": "Missing required fields"}',
                status_code=400,
                mimetype='application/json'
            )

        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return func.HttpResponse(
                '{"error": "User already exists"}',
                status_code=400,
                mimetype='application/json'
            )

        # Create user
        password_hash = hash_password(password)
        user_id = create_user(email, password_hash, name, 'consultant', specialty)

        # Generate token
        token = generate_token(user_id, email, 'consultant')

        return func.HttpResponse(
            json.dumps({
                'token': token,
                'user': {
                    'userId': user_id,
                    'email': email,
                    'name': name,
                    'role': 'consultant',
                    'specialty': specialty
                }
            }),
            status_code=201,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            mimetype='application/json'
        )


@app.route(route="auth/login", methods=["POST"])
def login(req: func.HttpRequest) -> func.HttpResponse:
    """Login a user."""
    try:
        body = req.get_json()
        email = body.get('email')
        password = body.get('password')

        if not email or not password:
            return func.HttpResponse(
                '{"error": "Missing email or password"}',
                status_code=400,
                mimetype='application/json'
            )

        # Get user
        user = get_user_by_email(email)
        if not user or not verify_password(password, user['PasswordHash']):
            return func.HttpResponse(
                '{"error": "Invalid credentials"}',
                status_code=401,
                mimetype='application/json'
            )

        # Generate token
        token = generate_token(str(user['UserId']), user['Email'], user['Role'])

        return func.HttpResponse(
            json.dumps({
                'token': token,
                'user': {
                    'userId': str(user['UserId']),
                    'email': user['Email'],
                    'name': user['Name'],
                    'role': user['Role'],
                    'specialty': user.get('Specialty')
                }
            }),
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            mimetype='application/json'
        )


# ============================================================================
# CASE MANAGEMENT ROUTES
# ============================================================================

@app.route(route="cases", methods=["POST"])
@require_auth
def create_new_case(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new theatre case."""
    try:
        user_id = req.user['user_id']
        case_data = req.get_json()

        # Validate required fields
        required_fields = ['procedureType', 'procedureName', 'datePerformed']
        if not all(field in case_data for field in required_fields):
            return func.HttpResponse(
                '{"error": "Missing required fields"}',
                status_code=400,
                mimetype='application/json'
            )

        case_id = create_case(user_id, case_data)

        return func.HttpResponse(
            json.dumps({'caseId': case_id, 'message': 'Case created successfully'}),
            status_code=201,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Create case error: {str(e)}")
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            mimetype='application/json'
        )


@app.route(route="cases", methods=["GET"])
@require_auth
def get_user_cases(req: func.HttpRequest) -> func.HttpResponse:
    """Get all cases for the authenticated user."""
    try:
        user_id = req.user['user_id']
        limit = int(req.params.get('limit', 100))
        offset = int(req.params.get('offset', 0))
        search_query = req.params.get('search')

        if search_query:
            cases = search_cases(user_id, search_query)
        else:
            cases = get_cases_by_user(user_id, limit, offset)

        # Convert datetime objects to strings
        for case in cases:
            for key, value in case.items():
                if hasattr(value, 'isoformat'):
                    case[key] = value.isoformat()

        return func.HttpResponse(
            json.dumps({'cases': cases}),
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Get cases error: {str(e)}")
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            mimetype='application/json'
        )


@app.route(route="cases/{caseId}", methods=["GET"])
@require_auth
def get_single_case(req: func.HttpRequest) -> func.HttpResponse:
    """Get a specific case by ID."""
    try:
        user_id = req.user['user_id']
        case_id = req.route_params.get('caseId')

        case = get_case_by_id(case_id, user_id)
        if not case:
            return func.HttpResponse(
                '{"error": "Case not found"}',
                status_code=404,
                mimetype='application/json'
            )

        # Convert datetime objects to strings
        for key, value in case.items():
            if hasattr(value, 'isoformat'):
                case[key] = value.isoformat()

        return func.HttpResponse(
            json.dumps({'case': case}),
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Get case error: {str(e)}")
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            mimetype='application/json'
        )


@app.route(route="cases/{caseId}", methods=["PUT"])
@require_auth
def update_existing_case(req: func.HttpRequest) -> func.HttpResponse:
    """Update an existing case."""
    try:
        user_id = req.user['user_id']
        case_id = req.route_params.get('caseId')
        case_data = req.get_json()

        success = update_case(case_id, user_id, case_data)
        if not success:
            return func.HttpResponse(
                '{"error": "Case not found or unauthorized"}',
                status_code=404,
                mimetype='application/json'
            )

        return func.HttpResponse(
            json.dumps({'message': 'Case updated successfully'}),
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Update case error: {str(e)}")
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            mimetype='application/json'
        )


@app.route(route="cases/{caseId}", methods=["DELETE"])
@require_auth
def delete_existing_case(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a case."""
    try:
        user_id = req.user['user_id']
        case_id = req.route_params.get('caseId')

        success = delete_case(case_id, user_id)
        if not success:
            return func.HttpResponse(
                '{"error": "Case not found or unauthorized"}',
                status_code=404,
                mimetype='application/json'
            )

        return func.HttpResponse(
            json.dumps({'message': 'Case deleted successfully'}),
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Delete case error: {str(e)}")
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            mimetype='application/json'
        )


# ============================================================================
# STATISTICS & ANALYSIS ROUTES
# ============================================================================

@app.route(route="statistics", methods=["GET"])
@require_auth
def get_statistics(req: func.HttpRequest) -> func.HttpResponse:
    """Get statistics for the user's cases."""
    try:
        user_id = req.user['user_id']

        # Get filter parameters
        filters = {}
        if req.params.get('procedureType'):
            filters['procedureType'] = req.params.get('procedureType')
        if req.params.get('startDate'):
            filters['startDate'] = req.params.get('startDate')
        if req.params.get('endDate'):
            filters['endDate'] = req.params.get('endDate')

        stats = get_case_statistics(user_id, filters)

        return func.HttpResponse(
            json.dumps({'statistics': stats}),
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Statistics error: {str(e)}")
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            mimetype='application/json'
        )


@app.route(route="query", methods=["POST"])
@require_auth
def custom_query(req: func.HttpRequest) -> func.HttpResponse:
    """Answer custom queries about cases using AI."""
    try:
        user_id = req.user['user_id']
        body = req.get_json()
        query = body.get('query')

        if not query:
            return func.HttpResponse(
                '{"error": "Missing query parameter"}',
                status_code=400,
                mimetype='application/json'
            )

        # Get all user's cases
        cases = get_cases_by_user(user_id, limit=1000)

        # Check if OpenAI is configured
        import os
        openai_key = os.environ.get('OPENAI_API_KEY')

        if openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)

                # Prepare case data summary for AI
                case_summary = prepare_case_summary(cases)

                # Call OpenAI
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are an analytical assistant helping a surgeon analyze their surgical cases.
                            Provide clear, data-driven insights based on the case data provided.
                            Be specific with numbers and percentages.
                            If the data doesn't support answering the question, say so clearly."""
                        },
                        {
                            "role": "user",
                            "content": f"Case Data:\n{case_summary}\n\nQuestion: {query}"
                        }
                    ],
                    temperature=0.7,
                    max_tokens=500
                )

                answer = response.choices[0].message.content

                return func.HttpResponse(
                    json.dumps({
                        'query': query,
                        'answer': answer,
                        'totalCases': len(cases),
                        'aiPowered': True
                    }),
                    status_code=200,
                    mimetype='application/json'
                )

            except Exception as ai_error:
                logging.error(f"OpenAI error: {str(ai_error)}")
                # Fall back to basic analysis
                pass

        # If OpenAI not available, provide basic analysis
        answer = analyze_query_locally(query, cases)

        return func.HttpResponse(
            json.dumps({
                'query': query,
                'answer': answer,
                'totalCases': len(cases),
                'aiPowered': False
            }),
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Query error: {str(e)}")
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            mimetype='application/json'
        )


def prepare_case_summary(cases: list) -> str:
    """Prepare a summary of cases for AI analysis."""
    if not cases:
        return "No cases available."

    summary = f"Total cases: {len(cases)}\n\n"

    # Procedure types
    procedure_types = {}
    for case in cases:
        pt = case.get('ProcedureType', 'Unknown')
        procedure_types[pt] = procedure_types.get(pt, 0) + 1

    summary += "Procedure Types:\n"
    for pt, count in procedure_types.items():
        summary += f"- {pt}: {count}\n"

    # Outcomes
    outcomes = {'positive': 0, 'neutral': 0, 'negative': 0, 'unknown': 0}
    for case in cases:
        outcome = case.get('Outcome', 'unknown')
        if outcome in outcomes:
            outcomes[outcome] += 1
        else:
            outcomes['unknown'] += 1

    summary += f"\nOutcomes:\n"
    for outcome, count in outcomes.items():
        summary += f"- {outcome.capitalize()}: {count}\n"

    # Complications
    with_complications = sum(1 for c in cases if c.get('Complications') and c['Complications'].lower() != 'none')
    summary += f"\nComplications: {with_complications} cases\n"

    # Average duration
    durations = [c.get('DurationMinutes') for c in cases if c.get('DurationMinutes')]
    if durations:
        avg_duration = sum(durations) / len(durations)
        summary += f"Average Duration: {avg_duration:.1f} minutes\n"

    # Include sample of actual cases (max 10) for context
    summary += "\nSample Cases:\n"
    for i, case in enumerate(cases[:10]):
        summary += f"{i+1}. {case.get('ProcedureName', 'Unknown')} - "
        summary += f"{case.get('ProcedureType', 'Unknown')} - "
        summary += f"Outcome: {case.get('Outcome', 'Unknown')} - "
        summary += f"Date: {case.get('DatePerformed', 'Unknown')}\n"

    return summary


def analyze_query_locally(query: str, cases: list) -> str:
    """Basic local query analysis when OpenAI is not available."""
    query_lower = query.lower()

    # Count-based queries
    if 'how many' in query_lower:
        if 'last' in query_lower and 'month' in query_lower:
            # Extract number of months
            import re
            months_match = re.search(r'(\d+)\s+month', query_lower)
            months = int(months_match.group(1)) if months_match else 3

            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(days=30 * months)

            recent = [c for c in cases if datetime.fromisoformat(c.get('DatePerformed', '2000-01-01').replace('Z', '+00:00')) >= cutoff]
            return f"You performed {len(recent)} cases in the last {months} months."

        if 'negative' in query_lower and 'margin' in query_lower:
            # This would require custom metrics - for now, general response
            return f"Based on {len(cases)} total cases. To track margin status specifically, add it as a custom metric when logging cases."

    # Rate-based queries
    if 'complication rate' in query_lower:
        with_comp = sum(1 for c in cases if c.get('Complications') and c['Complications'].lower() != 'none')
        rate = (with_comp / len(cases) * 100) if cases else 0
        return f"Your overall complication rate is {rate:.1f}% ({with_comp} out of {len(cases)} cases)."

    # Default response
    return f"I analyzed your {len(cases)} cases. For more advanced insights, configure the OpenAI API key in your environment variables."


# ============================================================================
# USER PROFILE ROUTES
# ============================================================================

@app.route(route="profile", methods=["GET"])
@require_auth
def get_profile(req: func.HttpRequest) -> func.HttpResponse:
    """Get user profile."""
    try:
        user_id = req.user['user_id']
        user = get_user_by_id(user_id)

        if not user:
            return func.HttpResponse(
                '{"error": "User not found"}',
                status_code=404,
                mimetype='application/json'
            )

        # Convert datetime to string
        if 'CreatedAt' in user and hasattr(user['CreatedAt'], 'isoformat'):
            user['CreatedAt'] = user['CreatedAt'].isoformat()

        return func.HttpResponse(
            json.dumps({'user': user}),
            status_code=200,
            mimetype='application/json'
        )

    except Exception as e:
        logging.error(f"Get profile error: {str(e)}")
        return func.HttpResponse(
            f'{{"error": "{str(e)}"}}',
            status_code=500,
            mimetype='application/json'
        )
