"""
author: @guu8hc
"""

from flask import render_template, request, jsonify, session as flask_session

from app.util import login_required
from app.util import get_git_branch

from . import wortschatz_bp
from .session_handler import SessionHandler


# Initialize the session handler
session_handler = SessionHandler()

@wortschatz_bp.route('/modes')
@login_required
def modes():
    """
    Render the wortschatz page template.

    Endpoint: wortschatz/modes

    Returns:
        str: The rendered HTML of the home page.
    """
    return render_template('wortschatz/modes.html', gitv=get_git_branch())

# Requirement: get_question
# Requester  : @Lyon
@wortschatz_bp.route('/session', methods=['GET'])
@login_required
def session():
    """
    Render the session page template.
    
    Endpoint: wortschatz/session?questions=<questions>&topic=<topic>
    e.g.    : wortschatz/session?questions=10&topic=car

    Args (from query parameters):
        questions (int): The number of questions to retrieve.
        topic     (str): The topic/keyword to search for.
    Returns:
        str: The rendered HTML of the session page.
    """
    # Extract query parameters
    questions = request.args.get('questions', type=int)
    topic = request.args.get('topic')

    # If no parameters provided, render page with empty data and let JavaScript handle defaults
    if questions is None and topic is None:
        return render_template('wortschatz/session.html', 
                             gitv=get_git_branch(),
                             words=[],
                             questions_data={},
                             questions=None,
                             topic=None)

    # Setup session handler with provided parameters
    session_handler.set_session(questions=questions, topic=topic)

    # Store questions in Flask session for validation endpoint
    flask_session['questions_data'] = session_handler.questions
    print(f"[DEBUG] Stored questions in session: {list(session_handler.questions.keys())}")

    # Retrieve session questions
    words = session_handler.get_questions()
    
    return render_template('wortschatz/session.html', 
                         gitv=get_git_branch(),
                         words=words,
                         questions_data=session_handler.questions,
                         questions=questions,
                         topic=topic)

# Requirement: submit_answer
# Requester  : @Lyon
@wortschatz_bp.route('/session/validate', methods=['GET'])
@login_required
def session_validate():
    """
    Validate the session data.
    
    Endpoint: wortschatz/session/validate?question=<question>&answer=<answer>
    e.g.    : wortschatz/session/validate?question=cat&answer=die%20Katze
    
    Returns:
        str: The rendered HTML of the session validation page.
    """
    # Extract query parameters
    question = request.args.get('question')
    answer = request.args.get('answer')
    
    print(f"[DEBUG] Validation request: question='{question}', answer='{answer}'")

    # Get questions from Flask session
    session_questions = flask_session.get('questions_data', {})
    print(f"[DEBUG] Available questions in session: {list(session_questions.keys())}")
    
    if not session_questions:
        print("[DEBUG] No questions found in session")
        return jsonify({'error': 'No active session found. Please reload the page.'})
    
    # Create temporary session handler with stored questions
    temp_handler = SessionHandler()
    temp_handler.questions = session_questions
    
    # Validation via session handler
    try:
        result = temp_handler.validate(question, answer)
        print(f"[DEBUG] Validation result: {result}")
        return jsonify({'result': result})
    except KeyError as e:
        print(f"[DEBUG] KeyError in validation: {e}")
        return jsonify({'error': f'Question not found: {question}', 'available_questions': list(session_questions.keys())})
    except Exception as e:
        print(f"[DEBUG] Validation error: {e}")
        return jsonify({'error': f'Validation failed: {str(e)}'})
