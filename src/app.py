# src/app.py
"""Flask application handling HTTP requests for booking meeting rooms."""

import uuid
from flask import Flask, request, render_template, session, redirect, url_for
from booking_agent.workflow import create_workflow
from helper import dict_to_message, message_to_dict
from config import FlaskConfig

app = Flask(__name__)
app.config.from_object(FlaskConfig)

# Initialize workflow
workflow = create_workflow()

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

    if 'agent_state' not in session:
        # Initialize a new session
        session['session_id'] = str(uuid.uuid4())
        session['agent_state'] = {
            'user_input': request.form['user_input'],
            'llm_response': None,
            'messages': [],
            'parsed_request': None,
            'clarification_needed': False,
            'clarification_question': None,
            'user_name_for_booking': None,
            'matching_rooms': None,
            'available_room_options': None,
            'selected_room_option_id': None,
            'user_booking_confirmation_response': None,
            'booking_result': None,
            'error_message': None
        }
    else:
        # Load existing session
        # Update user input in the session
        session['agent_state']['user_input'] = request.form['user_input']
        # Convert serialized messages (JSON) back to objects for LLM response
        session['agent_state']['messages'] = [dict_to_message(msg) for msg in session['agent_state']['messages']]

    ######################## Process through workflow ########################
    response = workflow.invoke(session['agent_state'])
    # 1. save LLM response to agent state in the session
    session['agent_state']['llm_response'] = str(response)
    
    # 2. Convert messages to serializable format (JSON) for Flask session
    session['agent_state']['messages'] = [message_to_dict(msg) for msg in session['agent_state']['messages']]
    session.modified = True
    return render_template('index.html', response=response)

# if __name__ == '__main__':
#     app.run(debug=app.config['DEBUG'])