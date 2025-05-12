# src/app.py
"""Flask application handling HTTP requests for booking meeting rooms."""

import uuid
from flask import Flask, request, render_template, session, redirect, url_for
from booking_agent.workflow import create_workflow
from helper import DEFAULT_AGENT_STATE, dict_to_message, message_to_dict
from config import FlaskConfig

app = Flask(__name__)
app.config.from_object(FlaskConfig)

# Initialize workflow
workflow = create_workflow()

@app.before_request
def initialize_session():
    """Ensure session and agent_state are properly initialized"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    if 'agent_state' not in session:
        session['agent_state'] = DEFAULT_AGENT_STATE.copy()

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('booking'))

@app.route('/booking', methods=['GET', 'POST'])
def booking():

    if request.method == 'GET':
        return render_template('index.html')
        
    # Load existing session
    # Update user input in the session
    session['agent_state']['user_input'] = request.form['user_input']
    # Convert serialized messages (JSON) back to objects for LLM response
    session['agent_state']['messages'] = [dict_to_message(msg) for msg in session['agent_state']['messages']]

    ######################## Process through workflow ########################
    response = workflow.invoke(session['agent_state'])
    # 1. save LLM response to agent state in the session and 
    # Extract only the latest assistant message
    assistant_message = None
    for msg in reversed(session['agent_state']['messages']):
        if msg.type == "system" or msg.type == "assistant":
            assistant_message = msg.content
            break    
    # 2. Convert messages to serializable format (JSON) for Flask session
    session['agent_state']['messages'] = [message_to_dict(msg) for msg in session['agent_state']['messages']]
    session.modified = True
    return render_template('index.html', response=assistant_message)

# if __name__ == '__main__':
#     app.run(debug=app.config['DEBUG'])