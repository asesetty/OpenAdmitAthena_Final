from flask import Flask, render_template, request, session, redirect, url_for
import openai
import os

from db_utils import load_students_data, save_students_data
from conversation_utils import (
    optimize_conversation_history,
    generate_messages,
    generate_conversation_starters,
    render_markdown
)

from competition_utils import (
    detect_science_project_request,
    detect_deca_request,
    generate_project_guidance,
    generate_deca_guidance
)

from mentor_utils import (
    should_recommend_mentor,
    recommend_mentor, generate_mentor_reason
)

app = Flask(__name__)
openai.api_key = "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"
app.secret_key = "IshaanIs2Freaky"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        student_id = request.form['name'].strip()
        if not student_id:
            return redirect(url_for('index'))

        students_data = load_students_data()

        if student_id not in students_data:
            students_data[student_id] = {
                'name': request.form['name'],
                'grade': request.form['grade'],
                'future_study': request.form['future_study'],
                'deep_interest': request.form['deep_interest'],
                'unique_something': request.form['unique_something'],
                'current_extracurriculars': request.form['current_extracurriculars'],
                'favorite_courses': request.form['favorite_courses'],

                # Additional fields we keep for ongoing data
                'competitions': [],
                'notes': []
            }
            save_students_data(students_data)

        session['student_id'] = student_id
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'student_id' not in session:
        return redirect(url_for('index'))

    students_data = load_students_data()
    student_id = session['student_id']
    student_info = students_data[student_id]

    # Session-level initialization
    if 'conversation' not in session:
        session['conversation'] = []
    if 'conversation_summary' not in session:
        session['conversation_summary'] = ""
    if 'mentor_cooldown' not in session:
        session['mentor_cooldown'] = 0
    if 'science_project_stage' not in session:
        session['science_project_stage'] = "none"
    if 'deca_stage' not in session:
        session['deca_stage'] = "none"

    conversation = session['conversation']
    conversation_summary = session['conversation_summary']

    if request.method == 'POST':
        user_message = request.form['message'].strip()
        if not user_message:
            return render_template('chat.html',
                                   conversation=conversation,
                                   starters=generate_conversation_starters(student_info, conversation),
                                   render_markdown=render_markdown)

        conversation.append({'role': 'user', 'content': user_message})

        conversation, conversation_summary = optimize_conversation_history(conversation, conversation_summary)

        # Check for special competition requests
        is_science_request = detect_science_project_request(user_message)
        is_deca_request = detect_deca_request(user_message)

        if session['science_project_stage'] == "clarifying":
            session['science_project_stage'] = "generate"
            conversation.append({
                'role': 'assistant',
                'content': "Got it. Let me think through a solid project idea for you..."
            })
            project_idea = generate_project_guidance(student_info, conversation)
            conversation.append({'role': 'assistant', 'content': project_idea})
            session['science_project_stage'] = "none"

        elif session['deca_stage'] == "clarifying":
            session['deca_stage'] = "generate"
            conversation.append({
                'role': 'assistant',
                'content': "Great, thanks for the details. Here's some DECA-specific guidance..."
            })
            deca_advice = generate_deca_guidance(student_info, conversation)
            conversation.append({'role': 'assistant', 'content': deca_advice})
            session['deca_stage'] = "none"

        elif is_science_request:
            session['science_project_stage'] = "clarifying"
            clarifying_msg = (
                "I'd love to help you with a science project! "
                "Could you tell me more about your interests? For example, do you prefer lab work, data analysis, or something else?"
            )
            conversation.append({'role': 'assistant', 'content': clarifying_msg})

        elif is_deca_request:
            session['deca_stage'] = "clarifying"
            clarifying_msg = (
                "Sure! DECA is great for developing business and marketing skills. "
                "Which events or areas do you have in mind? Finance, hospitality, marketing...?"
            )
            conversation.append({'role': 'assistant', 'content': clarifying_msg})

        else:
            assistant_message = _chat_with_athena(student_info, conversation, conversation_summary)
            conversation.append({'role': 'assistant', 'content': assistant_message})

            if session['mentor_cooldown'] > 0:
                session['mentor_cooldown'] -= 1
            else:
                if should_recommend_mentor(user_message):
                    best_mentor, best_score = recommend_mentor(user_message, student_info)
                    if best_mentor:
                        reason = generate_mentor_reason(best_mentor, user_message)
                        recommendation_text = (
                            f"I think you might benefit from chatting with Mentor **{best_mentor}** "
                            f"(similarity score: {best_score:.2f}).\n\n"
                            f"I recommended them because {reason}\n\n"
                            f"[Click here to chat with {best_mentor}]"
                        )
                        conversation.append({'role': 'assistant', 'content': recommendation_text})
                        session['mentor_cooldown'] = 5  # example

        session['conversation'] = conversation
        session['conversation_summary'] = conversation_summary

        starters = generate_conversation_starters(student_info, conversation)
        return render_template('chat.html',
                               conversation=conversation,
                               starters=starters,
                               render_markdown=render_markdown)

    else:
        session['conversation'] = []
        session['conversation_summary'] = ""
        session['mentor_cooldown'] = 0
        session['science_project_stage'] = "none"
        session['deca_stage'] = "none"

        starters = generate_conversation_starters(student_info, [])
        return render_template('chat.html',
                               conversation=[],
                               starters=starters,
                               render_markdown=render_markdown)

def _chat_with_athena(student_info, conversation, conversation_summary):
    from conversation_utils import generate_messages
    messages_for_model = generate_messages(student_info, conversation, conversation_summary)

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages_for_model,
        max_tokens=300,
        temperature=0.8
    )
    return response.choices[0].message.content.strip()

if __name__ == '__main__':
    app.run(debug=True)
