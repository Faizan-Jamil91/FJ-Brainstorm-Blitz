import streamlit as st
import google.generativeai as genai

class TestGenerator:
    def __init__(self):
        self.api_key = "AIzaSyBhppYwUZpoD8mqhnJ2ZLl1asuF957gFlU"  # Replace with your API key
        self.generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
        self.model = genai.GenerativeModel(model_name="gemini-pro",
                                          generation_config=self.generation_config,
                                          safety_settings=self.safety_settings)

    def generate_mcqs(self, designation):
        prompt = f"Generate 20 MCQs related to {designation}. Each question should test a key concept or skill associated with {designation}."
        response = self.model.generate_content(prompt, api_key=self.api_key)
        return response.text

    def check_answers(self, mcqs, answers):
        prompt = "Generate a summary based on the following MCQs and collected answers:\n\n"
        prompt += "Total MCQs:\n"
        prompt += "\n".join(mcqs)
        prompt += "\n\nCheck collected answers in the list below one by one:\n"
        prompt += "\n".join(answers)
        prompt += "\n"
        response = self.model.generate_content(prompt, api_key=self.api_key)
        result_lines = response.strip().split('\n')
        score = 0
        for i, (generated_mcq, collected_answer) in enumerate(zip(result_lines[:20], answers)):
            if generated_mcq.strip() == collected_answer.strip():
                score += 1
        return result, score

    def generate_suggestions(self, mcqs, answers, result):
        mcqs_text = "\n".join(mcqs)
        answers_text = "\n".join(answers)
        suggestions_input = f"Generate suggestions for learning based on the following:\n\nMCQs:\n{mcqs_text}\n\nCollected Answers:\n{answers_text}\n\nGenerated Result:\n{result}\n"
        suggestions = self.model.generate_content(suggestions_input, api_key=self.api_key)
        return suggestions

def main():
    result = None
    
    st.markdown("""
    <div style="text-align: center;">
    <h1>FJ Brainstorm Blitz</h1>
    </div>
    """, unsafe_allow_html=True)

    # Add the introductory paragraph
    st.markdown("""
    <div style="text-align: center;">
    FJ Brainstorm Blitz is a dynamic application revolutionizing the creation of multiple-choice questions (MCQs), tailored to users' expertise and interests. By entering their designation or preferred topic, users prompt the app to generate a customized set of MCQs. FJ Brainstorm Blitz not only facilitates quiz creation but also fosters learning through personalized suggestions based on user-generated questions and answers. With its user-friendly interface and AI-powered features, FJ Brainstorm Blitz aims to elevate learning experiences and promote knowledge acquisition across various disciplines and educational contexts.
    </div>
    """, unsafe_allow_html=True)

    info_generator = TestGenerator()

    # CSS styles
    st.markdown("""
    <style>
    .title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    .subheader {
        font-size: 18px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .text-input {
        width: 300px;
        margin-bottom: 10px;
    }

    .mcq-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
    }

    .mcq-input {
        width: 200px;
        margin-bottom: 10px;
    }

    .button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'mcqs' not in st.session_state:
        st.session_state.mcqs = None

    designation_input = st.text_input("Enter your designation:")

    if st.button("Generate MCQs") and designation_input:
        with st.spinner('Generating MCQs...'):
            st.session_state.mcqs = info_generator.generate_mcqs(designation_input)
        st.write("MCQs generated successfully!")

    if st.session_state.mcqs:
        st.subheader("Generated MCQs:")
        st.write(st.session_state.mcqs)

        collected_answers = []

        st.subheader("Enter Answers for the MCQs:")
        columns = st.columns(4)
        for i in range(20):
            with columns[i % 4]:
                answer_input = st.text_input(f"Answer for MCQ {i+1}:")
                collected_answers.append(answer_input)

        if st.button("Generate Result"):
            with st.spinner('Generating Result...'):
                result, score = info_generator.check_answers(st.session_state.mcqs, collected_answers)
        
            st.subheader("Generated Result:")
            st.write(result)
    
            # Display score
            st.subheader("Score:")
            st.write(f"{score} correct out of 20")


        if st.button("Generate Suggestions Result"):
            with st.spinner('Generating Suggestions...'):
                suggestions = info_generator.generate_suggestions(st.session_state.mcqs, collected_answers, result)
            st.subheader("Suggestions for Learning:")
            st.write(suggestions)

if __name__ == "__main__":
    main()
