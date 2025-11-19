import streamlit as st
import google.generativeai as genai
import pandas as pd
import re

class TestGenerator:
    def __init__(self):
        try:
            # Securely fetch API key from Streamlit secrets
            self.api_key = "AIzaSyApPXMTraGt1wwlr5wpRkGImIBSkMM5LJU"
            genai.configure(api_key=self.api_key)
            
            self.generation_config = {
                "temperature": 0.85,
                "top_p": 1,
                "top_k": 40,
                "max_output_tokens": 4096,
            }

            self.safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]

            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
        except Exception as e:
            st.error(f"Initialization error: {str(e)}")
            st.stop()

    def generate_content(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            if response.candidates and response.candidates[0].content.parts:
                return response.text
            st.error("No content generated. Please try again.")
            return None
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None


def parse_questions(response_text):
    """Parse generated questions into a structured format"""
    questions = []
    pattern = r'(\d+\.\s.*?)(?=\d+\.\s|\Z)'
    matches = re.findall(pattern, response_text, re.DOTALL)
    
    for match in matches:
        question_data = {"question": "", "options": []}
        lines = match.strip().split('\n')
        if lines:
            question_data["question"] = lines[0].strip()
            for line in lines[1:]:
                if re.match(r'^[A-D]\.\s', line.strip()):
                    question_data["options"].append(line.strip())
        if question_data["question"] and len(question_data["options"]) >= 2:
            questions.append(question_data)
            
    return questions[:20]  # Return max 20 questions


def display_questions(questions):
    """Display questions in a consistent format"""
    output = []
    for i, q in enumerate(questions, 1):
        output.append(f"{i}. {q['question']}")
        for option in q["options"]:
            output.append(f"   {option}")
        output.append("")
    return "\n".join(output)


def main():
    # Initialize session state variables
    if 'mcqs' not in st.session_state:
        st.session_state.mcqs = None
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'answer_key' not in st.session_state:
        st.session_state.answer_key = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = [''] * 20
    if 'results' not in st.session_state:
        st.session_state.results = None

    # UI Configuration
    st.set_page_config(
        page_title="JBS Brainstorm Blitz", 
        page_icon="🧠", 
        layout="centered"
    )

    # Header Section
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #2563EB;">🧠 JBS Brainstorm Blitz</h1>
        <p style="font-size: 1.1rem; color: #4B5563;">
        Revolutionizing MCQ creation with AI-powered learning experiences
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Introduction
    with st.expander("About this App", expanded=True):
        st.markdown("""
        **JBS Brainstorm Blitz** is a dynamic application that:
        
        - 🚀 Generates tailored multiple-choice questions based on your expertise
        - 📊 Evaluates your answers with detailed performance analysis
        - 💡 Provides personalized learning suggestions
        - 🎯 Helps you master topics efficiently
        
        Simply enter your topic of interest below to get started!
        """)

    # Initialize generator
    info_generator = TestGenerator()

    # Topic Input Section
    st.subheader("📚 Topic Selection")
    topic_input = st.text_input(
        "Enter your area of expertise or preferred topic:", 
        placeholder="e.g., Machine Learning, World History, Biology...",
        key="topic_input"
    )
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("✨ Generate MCQs", use_container_width=True):
            if not topic_input:
                st.warning("Please enter a topic first")
            else:
                with st.spinner('Generating questions...'):
                    prompt = (
                        f"Generate 20 comprehensive multiple-choice questions on {topic_input}. "
                        "Format each question with 4 options (A, B, C, D). "
                        "Ensure questions cover fundamental concepts and practical applications. "
                        "Do not include answers in the response."
                    )
                    response = info_generator.generate_content(prompt)
                    if response:
                        questions = parse_questions(response)
                        if questions:
                            st.session_state.questions = questions
                            st.session_state.mcqs = display_questions(questions)
                            st.session_state.user_answers = [''] * len(questions)
                            st.success(f"✅ Generated {len(questions)} questions!")
                        else:
                            st.error("Failed to parse questions. Please try again.")
    
    with col2:
        if st.session_state.mcqs and st.button("🔄 Regenerate MCQs", use_container_width=True):
            with st.spinner('Generating new questions...'):
                prompt = (
                    f"Generate a new set of 20 different multiple-choice questions on {topic_input}. "
                    "Format each question with 4 options (A, B, C, D). "
                    "Ensure questions are distinct from previous ones."
                )
                response = info_generator.generate_content(prompt)
                if response:
                    questions = parse_questions(response)
                    if questions:
                        st.session_state.questions = questions
                        st.session_state.mcqs = display_questions(questions)
                        st.session_state.user_answers = [''] * len(questions)
                        st.session_state.results = None
                        st.success(f"✅ Generated {len(questions)} new questions!")

    # Display Generated Questions
    if st.session_state.mcqs:
        st.subheader("📝 Generated Questions")
        with st.expander("View Questions", expanded=True):
            st.text_area("Questions", st.session_state.mcqs, height=400, disabled=True)
        
        # Answer Input Section
        st.subheader("📥 Enter Your Answers")
        st.info("Select answers for each question below. Scroll to see all questions.")
        
        # Create answer input columns
        cols = st.columns(4)
        for i, question in enumerate(st.session_state.questions):
            with cols[i % 4]:
                options = [opt[0] for opt in question["options"]]
                st.session_state.user_answers[i] = st.radio(
                    f"Q{i+1}:",
                    options=options,
                    index=options.index(st.session_state.user_answers[i]) if st.session_state.user_answers[i] in options else 0,
                    key=f"answer_{i}"
                )
        
        # Results Generation
        st.subheader("📊 Results & Analysis")
        if st.button("🔍 Evaluate Answers", type="primary"):
            with st.spinner('Generating answer key and analysis...'):
                # Generate answer key
                questions_text = "\n".join([f"{i+1}. {q['question']}" for i, q in enumerate(st.session_state.questions)])
                prompt = (
                    f"For the following questions about {topic_input}, provide the correct answer for each question (only the letter):\n\n"
                    f"{questions_text}\n\n"
                    "Format your response as: 1. [LETTER], 2. [LETTER], ... 20. [LETTER]"
                )
                response = info_generator.generate_content(prompt)
                if response:
                    # Parse answer key
                    answer_key = re.findall(r'[A-D]', response.upper())
                    if len(answer_key) >= len(st.session_state.questions):
                        st.session_state.answer_key = answer_key[:len(st.session_state.questions)]
                        
                        # Calculate results
                        correct = 0
                        results = []
                        for i in range(len(st.session_state.questions)):
                            is_correct = st.session_state.user_answers[i] == st.session_state.answer_key[i]
                            correct += 1 if is_correct else 0
                            results.append({
                                "Question": i+1,
                                "Your Answer": st.session_state.user_answers[i],
                                "Correct Answer": st.session_state.answer_key[i],
                                "Result": "✅ Correct" if is_correct else "❌ Incorrect"
                            })
                        
                        # Store results
                        st.session_state.results = {
                            "score": correct,
                            "total": len(st.session_state.questions),
                            "details": pd.DataFrame(results)
                        }
                    else:
                        st.error("Failed to parse answer key. Please try again.")

        # Display Results
        if st.session_state.results:
            res = st.session_state.results
            score_percent = (res["score"] / res["total"]) * 100
            
            st.metric("Your Score", f"{res['score']}/{res['total']} ({score_percent:.1f}%)")
            
            # Performance gauge
            gauge_color = "green" if score_percent >= 70 else "orange" if score_percent >= 50 else "red"
            st.markdown(f"""
            <div style="background: #F3F4F6; border-radius: 10px; padding: 15px; margin: 15px 0;">
                <div style="font-weight: bold; margin-bottom: 5px;">Performance:</div>
                <div style="height: 20px; background: #E5E7EB; border-radius: 10px;">
                    <div style="height: 100%; width: {score_percent}%; background: {gauge_color}; border-radius: 10px;"></div>
                </div>
                <div style="text-align: center; margin-top: 5px; font-size: 0.9rem;">
                    {score_percent:.1f}% Correct
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Results table
            with st.expander("Detailed Results", expanded=True):
                st.dataframe(res["details"], hide_index=True)
            
            # Learning Suggestions
            st.subheader("💡 Learning Suggestions")
            if st.button("Get Personalized Study Plan"):
                with st.spinner("Generating learning suggestions..."):
                    # Identify weak areas
                    incorrect = res["details"][res["details"]["Result"] == "❌ Incorrect"]
                    weak_areas = ", ".join([str(q) for q in incorrect["Question"].tolist()]) if not incorrect.empty else "None"
                    
                    prompt = (
                        f"The user scored {res['score']}/{res['total']} on a {topic_input} quiz. "
                        f"They struggled with questions: {weak_areas}. "
                        "Provide concise, actionable learning suggestions to improve their understanding. "
                        "Recommend specific resources, concepts to review, and practice strategies. "
                        "Structure the response with clear headings and bullet points."
                    )
                    
                    suggestions = info_generator.generate_content(prompt)
                    if suggestions:
                        st.markdown("### Personalized Study Recommendations")
                        st.markdown(suggestions)
                    else:
                        st.warning("Could not generate suggestions. Please try again.")

    # Footer
    st.markdown("---")
    st.caption("© 2024 JBS Brainstorm Blitz | AI-Powered Learning Assistant")


if __name__ == "__main__":
    main()



