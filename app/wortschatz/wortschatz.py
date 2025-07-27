"""
author: @guu8hc
"""

from flask import render_template, request, jsonify

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

    Args (from query parameters):
        questions (int): The number of questions to retrieve.
        topic     (str): The topic/keyword to search for.
    Returns:
        str: The rendered HTML of the session page.
    """
    # Extract query parameters
    questions = request.args.get('questions', type=int)
    topic = request.args.get('topic')

    # Setup session handler
    session_handler.set_session(questions=questions, topic=topic)

    # Retrieve session questions
    words = session_handler.get_questions()
    
    return render_template('wortschatz/session.html', 
                         gitv=get_git_branch(),
                         words=words,
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

    # Validation via session handler
    result = session_handler.validate(question, answer) if session_handler else None

    return jsonify({'result': result}) if result is not None else jsonify({'error': 'Session handler not initialized'})
