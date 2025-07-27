"""
author: @guu8hc
"""

from flask import render_template, request

from app.util import login_required
from app.util import get_git_branch

from app.database import deen_db

from . import wortschatz_bp


@wortschatz_bp.route('/modes')
@login_required
def modes():
    """
    Render the wortschatz page template.
    Returns:
        str: The rendered HTML of the home page.
    """
    return render_template('wortschatz/modes.html', gitv=get_git_branch())

@wortschatz_bp.route('/session')
@login_required
def session():
    """
    Render the session page template.
    Args (from query parameters):
        questions (int): The number of questions to retrieve.
        topic (str): The topic/keyword to search for.
    Returns:
        str: The rendered HTML of the session page.
    """
    questions = request.args.get('questions', type=int)
    topic = request.args.get('topic')
    
    # Handle missing or invalid parameters
    if not questions or not topic:
        # You might want to redirect to an error page or back to modes
        return render_template('wortschatz/modes.html', 
                             gitv=get_git_branch(),
                             error="Missing questions or topic parameter")
    
    if topic == "random":
        # If the topic is 'random', retrieve random words
        words = deen_db.get_random_word(questions)
    else:    
        # Retrieve words based on the topic
        words = deen_db.get_questions_by_keyword(questions, topic)

    print(f"[DEBUG] Retrieved {len(words)} words for topic '{topic}' with {questions} questions.")
    return render_template('wortschatz/session.html', 
                         gitv=get_git_branch(),
                         words=words,
                         questions=questions,
                         topic=topic)
