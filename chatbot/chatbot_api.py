import re
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict

from chatbot.conversation_manager import get_session
from chatbot.gemini_service import generate_response

# Try importing RAG retrieve safely
try:
    from chatbot.rag.retriever import retrieve
except Exception as e:
    print(f"[Chatbot API] RAG retrieve failed to import: {e}. Running with mock retriever.")
    retrieve = None

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

CATEGORY_QUESTIONS = {
    "❤️ Love": [
        "❤️ Will I find true love?",
        "💕 Is my partner loyal?",
        "💍 When will I get married?",
        "💌 Will my ex return?",
        "🌹 Best day for a date?",
        "💖 Should I confess my feelings?",
        "📱 Should I message first?",
        "💑 Is my relationship compatible?",
    ],
    "💍 Marriage": [
        "💍 When will I get married?",
        "❤️ Love or Arranged Marriage?",
        "👰 Who is my ideal life partner?",
        "💕 Marriage Compatibility",
        "📅 Best Marriage Date",
        "💖 Married Life Prediction",
        "⚠ Marriage Delay Reasons",
        "🌸 Marriage Success Prediction",
    ],
    "💼 Career": [
        "📈 Will I get promoted?",
        "💼 Should I change my job?",
        "💰 Salary Growth",
        "🏢 Government Job",
        "🌍 Abroad Opportunity",
        "🚀 Business or Job?",
        "⭐ Best Career Path",
        "📅 Best Time to Switch Jobs",
    ],
    "🎓 Education": [
        "📚 Will I succeed in exams?",
        "🎓 Which course suits me?",
        "✈ Study Abroad",
        "📝 Competitive Exams",
        "📖 Higher Education",
        "🏆 Best Study Time",
        "💡 Improve Studies",
        "🎯 Best Career Stream",
    ],
    "💰 Business": [
        "📈 Business Growth",
        "💸 Profit Prediction",
        "🏢 Start New Business",
        "🤝 Partnership Success",
        "📅 Best Launch Date",
        "💎 Lucky Business Name",
        "🌍 Business Expansion",
        "📊 Investment Success",
    ],
}

GUIDANCE_CATEGORIES = list(CATEGORY_QUESTIONS.keys())
PREDICTION_TYPES = [
    "🔮 Today (FREE)",
    "📅 Weekly (Premium) 🔒",
    "📆 Monthly (Premium) 🔒",
    "📈 Yearly (Premium) 🔒",
    "⭐ Lifetime (Premium) 🔒",
]
PREMIUM_TYPES = set(PREDICTION_TYPES[1:])
TOTAL_STEPS = 6

SERVICES = [
    {"title": "🔢 Number Numerology", "url": "https://asbreports.in/"},
    {"title": "📱 Mobile Numerology", "url": "https://mobile.asbreports.in/"},
    {"title": "✨ Name Numerology", "url": "https://name.asbreports.in/"},
    {"title": "🃏 Tarot Reading", "url": "https://asbreports.in/tarot"},
    {"title": "📞 Consultation", "url": "https://asbreports.in/consult"},
    {"title": "🛒 Marketplace", "url": "https://asbcrystal.in/"},
    {"title": "👤 Complete Profile", "url": "https://asbreports.in/complete-profile"},
]


def button_only(answer, buttons, step=None):
    response = {
        "answer": answer,
        "buttons": buttons,
        "input_type": "button_only",
    }
    if step:
        response["step"] = step
        response["total_steps"] = TOTAL_STEPS
    return response


def text_prompt(answer, input_type="text", step=None, placeholder="Type here..."):
    response = {
        "answer": answer,
        "input_type": input_type,
        "placeholder": placeholder,
    }
    if step:
        response["step"] = step
        response["total_steps"] = TOTAL_STEPS
    return response


def choice_key(value):
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def normalize_choice(message, choices):
    msg = message.strip().lower()
    msg_key = choice_key(msg)
    for choice in choices:
        choice_lower = choice.lower()
        current_key = choice_key(choice)
        if msg == choice_lower or msg in choice_lower or choice_lower in msg:
            return choice
        if msg_key and (msg_key == current_key or msg_key in current_key or current_key in msg_key):
            return choice
    return None


def clean_prediction(answer):
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    bullets = []

    for line in lines:
        if line.startswith(("-", "•", "*")):
            bullets.append("• " + line.lstrip("-•* ").strip())
        elif ":" in line and len(bullets) < 5:
            bullets.append("• " + line.strip())

    labels = ["Today's Energy", "Lucky Number", "Lucky Color", "Positive Advice", "Things to Avoid"]
    fallback = [
        "• Today's Energy: Positive and productive.",
        "• Lucky Number: 3",
        "• Lucky Color: Yellow",
        "• Positive Advice: Stay focused and trust your intuition.",
        "• Things to Avoid: Overthinking and unnecessary stress.",
    ]

    final = []
    for index in range(5):
        if index < len(bullets):
            text = bullets[index]
            if labels[index].lower() not in text.lower():
                text = f"• {labels[index]}: {text.lstrip('• ').strip()}"
            final.append(text)
        else:
            final.append(fallback[index])

    return "🔮 Today's Prediction\n\n" + "\n".join(final[:5])


def reduce_number(value):
    total = sum(int(char) for char in value if char.isdigit())
    while total > 9:
        total = sum(int(char) for char in str(total))
    return total or 3


def generate_today_prediction(data):
    lucky_number = reduce_number(data.get("dob", ""))
    colors = ["Yellow", "White", "Gold", "Green", "Blue", "Pink", "Purple", "Orange", "Red"]
    lucky_color = colors[(lucky_number - 1) % len(colors)]

    return clean_prediction(
        f"""
• Today's Energy: Positive and productive.
• Lucky Number: {lucky_number}
• Lucky Color: {lucky_color}
• Positive Advice: Stay focused and trust your intuition.
• Things to Avoid: Overthinking and unnecessary stress.
"""
    )


def initialize_guided_flow(session, user_profile=None):
    session["intent"] = "guided_numerology"
    session["data"] = {}
    
    # Check if we have valid user profile fields
    if user_profile and user_profile.get("name") and user_profile.get("dob"):
        session["data"]["name"] = user_profile.get("name")
        session["data"]["dob"] = user_profile.get("dob")
        
        # Standardize gender if available
        gender_raw = user_profile.get("gender", "Other").strip().lower()
        if "female" in gender_raw:
            gender = "Female"
        elif "male" in gender_raw:
            gender = "Male"
        else:
            gender = "Other"
            
        session["data"]["gender"] = gender
        session["step"] = 4
        
        return button_only(
            f"🙏 Namaste, {user_profile.get('name')}!\n\nI have retrieved your profile details (DOB: {user_profile.get('dob')}).\n\nWhat would you like guidance on today?",
            GUIDANCE_CATEGORIES,
            4
        )
    else:
        session["step"] = 1
        return text_prompt("👤 Please enter your Full Name.", "text", 1, "Type your full name...")


def get_chat_response(message: str, session_id: str = "default", user_profile: dict = None):
    session = get_session(session_id)
    msg = message.strip()
    msg_lower = msg.lower()

    if "history" not in session:
        session["history"] = []
    session["history"].append({"role": "user", "content": message})

    # Start over / reset keywords
    if msg_lower in {"start over", "restart", "reset", "name correction", "start"}:
        response = initialize_guided_flow(session, user_profile)
        session["history"].append({"role": "bot", "content": response["answer"]})
        return response

    # If the user is NOT currently in a guided flow
    if session.get("intent") != "guided_numerology":
        # Check if they want to initiate guided flow
        if msg_lower in {"guided reading", "get guided reading", "guided numerology reading", "guided", "1", "guided flow"}:
            response = initialize_guided_flow(session, user_profile)
            session["history"].append({"role": "bot", "content": response["answer"]})
            return response
        else:
            # Treat as free-form QA search
            context_chunks = []
            if retrieve is not None:
                try:
                    context_chunks = retrieve(msg, n_results=3)
                except Exception as re_err:
                    print(f"[Chatbot] RAG retrieval failed: {re_err}")
            
            context_text = "\n---\n".join(context_chunks) if context_chunks else "No specific document found in database."
            
            prompt = f"""You are the ASB AI Advisor, a helpful and friendly numerology advisor for ASB Numerology.
Use the following context from our knowledge base (about refund policies, about us, career reports, mobile numerology, name correction, etc.) to answer the user's question.
If the context doesn't contain the information or if you don't know the answer, answer the question politely using general numerology knowledge or refer them to our services. Keep the answer concise (2-4 sentences max), inspiring, and formatted nicely.

Context:
{context_text}

User Question: {msg}
Answer:"""
            try:
                answer = generate_response(prompt)
            except Exception as llm_err:
                print(f"[Chatbot] LLM response generation failed: {llm_err}")
                answer = "I'm sorry, I had trouble generating a response. Please ask something else or trigger our guided flow."

            response = {
                "answer": answer,
                "input_type": "text",
                "buttons": ["🔮 Get Guided Reading", "📞 Book Consultation"],
                "step": 0,
                "total_steps": TOTAL_STEPS
            }
            session["history"].append({"role": "bot", "content": response["answer"]})
            return response

    # Guided flow step execution
    step = session.get("step", 1)
    data = session.setdefault("data", {})

    if step == 1:
        data["name"] = msg
        session["step"] = 2
        response = text_prompt("📅 Please select your Date of Birth.", "date", 2)
    elif step == 2:
        data["dob"] = msg
        session["step"] = 3
        response = button_only("👤 Please choose your Gender.", ["🧘 Male", "🧘‍♀️ Female", "⚧ Other"], 3)
    elif step == 3:
        gender = normalize_choice(msg, ["Male", "Female", "Other", "🧘 Male", "🧘‍♀️ Female", "⚧ Other"])
        if not gender:
            response = button_only("👤 Please choose your Gender.", ["🧘 Male", "🧘‍♀️ Female", "⚧ Other"], 3)
        else:
            data["gender"] = gender.replace("🧘‍♀️ ", "").replace("🧘 ", "").replace("⚧ ", "")
            session["step"] = 4
            response = button_only("✨ What would you like guidance on today?", GUIDANCE_CATEGORIES, 4)
    elif step == 4:
        category = normalize_choice(msg, GUIDANCE_CATEGORIES)
        if not category:
            response = button_only("✨ What would you like guidance on today?", GUIDANCE_CATEGORIES, 4)
        else:
            data["category"] = category
            session["step"] = 5
            response = button_only(f"{category.split(' ', 1)[0]} What would you like to know?", CATEGORY_QUESTIONS[category], 5)
    elif step == 5:
        category = data.get("category")
        questions = CATEGORY_QUESTIONS.get(category, [])
        data["selected_question"] = normalize_choice(msg, questions) or msg
        session["step"] = 6
        response = button_only("✨ Which type of prediction would you like?", PREDICTION_TYPES, 6)
    elif step == 6:
        prediction_type = normalize_choice(msg, PREDICTION_TYPES)
        if not prediction_type:
            response = button_only("✨ Which type of prediction would you like?", PREDICTION_TYPES, 6)
        elif prediction_type in PREMIUM_TYPES:
            response = button_only(
                "🔒 Premium Feature\n\nUpgrade to unlock Weekly, Monthly, Yearly and Lifetime Predictions.",
                ["🔮 Today (FREE)"],
                6,
            )
        else:
            data["prediction_type"] = prediction_type
            answer = generate_today_prediction(data)
            response = {
                "answer": answer + "\n\n✨ Recommended ASB Services\nYou may also explore:",
                "type": "service_cards",
                "services": SERVICES,
                "input_type": "button_only",
                "step": TOTAL_STEPS,
                "total_steps": TOTAL_STEPS,
                "profileComplete": True,
            }
            # Capture lead detail when complete!
            try:
                from chatbot.lead_service import save_lead
                save_lead({
                    "name": data.get("name"),
                    "dob": data.get("dob"),
                    "gender": data.get("gender"),
                    "category": data.get("category"),
                    "selected_question": data.get("selected_question"),
                    "intent": "guided_numerology"
                })
            except Exception as le_err:
                print(f"[Chatbot] Save lead failed: {le_err}")

            # Reset session after completion
            session["intent"] = None
            session["step"] = 0
            session["data"] = {}
    else:
        response = start_guided_flow(session)

    session["history"].append({"role": "bot", "content": response["answer"]})
    return response


# --- API Routes ---

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    user_profile: Optional[Dict] = None


@router.post("/chat")
def chat(request: ChatRequest):
    return get_chat_response(
        request.message,
        request.session_id,
        request.user_profile
    )


@router.post("/rebuild-db")
def rebuild_db():
    try:
        from chatbot.rag.vector_store import build_vector_store
        build_vector_store()
        return {"success": True, "message": "Chroma DB rebuilt successfully."}
    except Exception as e:
        return {"success": False, "error": str(e)}