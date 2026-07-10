sessions = {}


def get_session(user_id="default"):

    if user_id not in sessions:

        sessions[user_id] = {
            "intent": None,
            "step": 0,
            "data": {},
            "history": []
        }

    return sessions[user_id]