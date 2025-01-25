# competition_utils.py

import openai

# Adjust model names if needed:
FINE_TUNED_SCIENCE_MODEL = "ADD HERE"
FINE_TUNED_DECA_MODEL = "gpt-4o"

def detect_science_project_request(user_message):
    prompt = (
        "You are an AI assistant that determines if a student's message is a request for help with a science project idea. "
        "The response should be exactly 'Yes' or 'No'.\n\n"
        f"Message: \"{user_message}\"\n\nIs this a request for help with a science project idea?"
    )
    response = openai.chat.completions.create(
        model="gpt-4",  
        messages=[{"role": "system", "content": prompt}],
        max_tokens=1,
        temperature=0
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer == 'yes'

def detect_deca_request(user_message):
    prompt = (
        "You are an AI assistant that determines if a student's message is a request for DECA competition advice. "
        "The response should be exactly 'Yes' or 'No'.\n\n"
        f"Message: \"{user_message}\"\n\nIs this a request for DECA competition advice?"
    )
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=1,
        temperature=0
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer == 'yes'

def generate_project_guidance(student_info, conversation):
    system_prompt = (
        "You are Athena, a friendly college counselor specializing in helping students develop award-winning science project ideas. "
        "Provide a detailed, innovative, unique project idea suitable for ISEF-level competitions, "
        "including proposed methods, specific datasets if relevant, and tailoring it to the student's profile. "
        "Use a conversational tone, format response in Markdown."
    )

    student_profile = (
        f"Student's Profile:\n"
        f"- Name: {student_info.get('name')}\n"
        f"- Grade: {student_info.get('grade')}\n"
        f"- Coursework: {student_info.get('coursework')}\n"
        f"- Favorite Subjects: {student_info.get('favorite_subjects')}\n"
        f"- In-school Organizations: {student_info.get('in_school_orgs')}\n"
        f"- Out-of-school Activities: {student_info.get('out_of_school')}\n"
        f"- Hobbies/Passions: {student_info.get('hobbies')}\n"
        f"- What they care about most: {student_info.get('care_about')}\n"
        f"- Values: {student_info.get('values')}\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": student_profile}
    ]
    messages.extend(conversation)

    response = openai.chat.completions.create(
        model=FINE_TUNED_SCIENCE_MODEL,  # or "gpt-4" if not fine-tuned
        messages=messages,
        max_tokens=600,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def generate_deca_guidance(student_info, conversation):
    system_prompt = (
        "You are Athena, an expert in DECA competitions. Provide guidance on preparing for DECA, "
        "including recommended practice materials, strategies for role-plays or written events, "
        "based on the student's profile. Use a friendly, conversational tone, Markdown formatting."
    )

    student_profile = (
        f"Student's Profile:\n"
        f"- Name: {student_info.get('name')}\n"
        f"- Grade: {student_info.get('grade')}\n"
        f"- Coursework: {student_info.get('coursework')}\n"
        f"- Favorite Subjects: {student_info.get('favorite_subjects')}\n"
        f"- In-school Organizations: {student_info.get('in_school_orgs')}\n"
        f"- Out-of-school Activities: {student_info.get('out_of_school')}\n"
        f"- Hobbies/Passions: {student_info.get('hobbies')}\n"
        f"- What they care about most: {student_info.get('care_about')}\n"
        f"- Values: {student_info.get('values')}\n"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": student_profile}
    ]
    messages.extend(conversation)

    response = openai.chat.completions.create(
        model=FINE_TUNED_DECA_MODEL,
        messages=messages,
        max_tokens=600,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()
