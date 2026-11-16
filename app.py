
import streamlit as st
import sqlite3
from groq import Groq
from pypdf import PdfReader

# Page configuration
st.set_page_config(
    page_title="StudyMate AI",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
.stButton button {
    border-radius: 10px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# Application title
st.title("🎓 StudyMate AI")
st.subheader("Your Personal Educational Virtual Assistant")
st.write("Learn smarter, prepare better and improve your productivity.")

# Groq API configuration
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception:
    st.error(
        "Groq API key not found. "
        "Configure .streamlit/secrets.toml correctly."
    )
    st.stop()

MODEL = "openai/gpt-oss-20b"


# AI response function
def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=2048
        )

        answer = response.choices[0].message.content

        if answer:
            return answer

        return "The AI did not return a response."

    except Exception as e:
        return f"AI Error: {str(e)}"


# Database setup
conn = sqlite3.connect(
    "studymate.db",
    check_same_thread=False
)

conn.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    task TEXT NOT NULL,
    status TEXT DEFAULT 'Pending'
)
""")

conn.commit()


# Sidebar navigation
st.sidebar.title("📚 StudyMate AI")

page = st.sidebar.radio(
    "Select a feature",
    [
        "Home",
        "AI Chat Assistant",
        "Notes Summarizer",
        "Quiz Generator",
        "Code Explainer",
        "Study Planner"
    ]
)


# Home page
if page == "Home":

    st.header("Welcome to StudyMate AI 👋")

    st.write(
        "Your AI-powered learning companion designed "
        "especially for college students."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.info("💬 AI Chat Assistant")
        st.info("📄 Notes Summarizer")
        st.info("📝 Quiz Generator")

    with col2:
        st.info("💻 Code Explainer")
        st.info("📅 Study Planner")

    st.success(
        "Select any feature from the sidebar to get started."
    )


# AI Chat Assistant
elif page == "AI Chat Assistant":

    st.header("💬 AI Chat Assistant")

    st.write("Ask any academic question.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask your question here...")

    if user_input:

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.write(user_input)

        history = "\n".join(
            f'{m["role"]}: {m["content"]}'
            for m in st.session_state.messages[-10:]
        )

        prompt = (
            "You are StudyMate AI, an educational assistant "
            "for college students. Explain concepts in simple "
            "language with examples. Help with engineering, "
            "programming, mathematics and other academic subjects.\n"
            + history
        )

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):
                answer = ask_ai(prompt)
                st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# Notes Summarizer
elif page == "Notes Summarizer":

    st.header("📄 Notes Summarizer")

    uploaded_file = st.file_uploader(
        "Upload your PDF notes",
        type=["pdf"]
    )

    if uploaded_file:

        if st.button("Summarize PDF"):

            try:
                reader = PdfReader(uploaded_file)

                if reader.is_encrypted:
                    st.error("Please upload an unlocked PDF.")

                else:

                    text = "\n".join(
                        page.extract_text() or ""
                        for page in reader.pages
                    )

                    if not text.strip():

                        st.warning(
                            "No readable text found. "
                            "This PDF may contain scanned images."
                        )

                    else:

                        with st.spinner("Preparing summary..."):

                            summary = ask_ai(
                                "Summarize these study notes. "
                                "Use headings, definitions, important "
                                "points and simple explanations.\n\n"
                                + text[:40000]
                            )

                        st.subheader("Your Summary")
                        st.markdown(summary)

            except Exception as e:
                st.error(f"PDF Error: {e}")


# Quiz Generator
elif page == "Quiz Generator":

    st.header("📝 AI Quiz Generator")

    topic = st.text_input(
        "Enter the topic",
        placeholder="Example: Binary Search"
    )

    difficulty = st.selectbox(
        "Choose difficulty",
        ["Easy", "Medium", "Hard"]
    )

    number = st.slider(
        "Number of questions",
        5, 15, 5
    )

    if st.button("Generate Quiz"):

        if topic.strip():

            prompt = f"""
            Generate {number} multiple choice questions
            about {topic}.
            Difficulty: {difficulty}.

            Give exactly four options for each question.
            Clearly mention the correct answer and a short
            explanation after each question.

            Use this format:

            Question 1:
            A.
            B.
            C.
            D.
            Correct Answer:
            Explanation:
            """

            with st.spinner("Generating your quiz..."):
                result = ask_ai(prompt)

            st.subheader("Your AI Generated Quiz")
            st.markdown(result)

        else:
            st.warning("Please enter a topic.")


# Code Explainer
elif page == "Code Explainer":

    st.header("💻 Code Explainer")

    language = st.selectbox(
        "Select programming language",
        ["C++", "Python", "Java"]
    )

    code = st.text_area(
        "Paste your program here",
        height=250,
        placeholder="Paste your code..."
    )

    if st.button("Explain Code"):

        if code.strip():

            prompt = f"""
            Explain this {language} program for a beginner.

            Include:
            1. Purpose of the program.
            2. Logic and working.
            3. Explanation of important lines.
            4. Example dry run.
            5. Time and space complexity if applicable.

            Code:
            {code}
            """

            with st.spinner("Analyzing your code..."):
                result = ask_ai(prompt)

            st.subheader("Code Explanation")
            st.markdown(result)

        else:
            st.warning("Please paste your code.")


# Study Planner
elif page == "Study Planner":

    st.header("📅 Personal Study Planner")

    st.write("Organize your daily study tasks.")

    with st.form("task_form"):

        subject = st.text_input("Subject")

        task = st.text_input("Study task")

        submitted = st.form_submit_button("Add Task")

        if submitted:

            if subject.strip() and task.strip():

                conn.execute(
                    "INSERT INTO tasks (subject, task) VALUES (?, ?)",
                    (subject.strip(), task.strip())
                )

                conn.commit()

                st.success("Task added successfully!")

            else:
                st.warning("Enter both subject and task.")

    st.divider()

    st.subheader("Your Study Tasks")

    tasks = conn.execute(
        "SELECT id, subject, task, status FROM tasks ORDER BY id DESC"
    ).fetchall()

    if not tasks:

        st.info("No tasks added yet.")

    for task_id, subject, task, status in tasks:

        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.write(f"**{subject}**")
            st.write(task)

        with col2:
            st.write(status)

        with col3:

            if status == "Pending":

                if st.button("Complete", key=f"complete_{task_id}"):

                    conn.execute(
                        "UPDATE tasks SET status='Completed' WHERE id=?",
                        (task_id,)
                    )

                    conn.commit()
                    st.rerun()

            else:
                st.success("Done")

        st.divider()


# Sidebar footer
st.sidebar.divider()
st.sidebar.caption("StudyMate AI | BTech Mini Project")

