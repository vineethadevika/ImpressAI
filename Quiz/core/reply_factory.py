from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST, CORRECT_ANSWERS

def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses

def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if current_question_id is None:
        return False, "Invalid question ID."

    if not answer.strip():
        return False, "Answer cannot be empty."

    user_answers = session.get("user_answers", {})
    user_answers[current_question_id] = answer
    session["user_answers"] = user_answers
    return True, ""

def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None:
        next_question = PYTHON_QUESTION_LIST[0]
        return next_question["question"], next_question["id"]

    for index, question in enumerate(PYTHON_QUESTION_LIST):
        if question["id"] == current_question_id:
            if index + 1 < len(PYTHON_QUESTION_LIST):
                next_question = PYTHON_QUESTION_LIST[index + 1]
                return next_question["question"], next_question["id"]
            else:
                return None, None

    return None, None

def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get("user_answers", {})
    score = 0
    total_questions = len(PYTHON_QUESTION_LIST)

    for question in PYTHON_QUESTION_LIST:
        question_id = question["id"]
        correct_answer = CORRECT_ANSWERS.get(question_id)
        user_answer = user_answers.get(question_id)

        if user_answer == correct_answer:
            score += 1

    response = f"You answered {score} out of {total_questions} questions correctly."
    return response
