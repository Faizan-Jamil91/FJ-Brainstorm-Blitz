import streamlit as st
import google.generativeai as genai
import pandas as pd

class TestGenerator:
    def __init__(self):
        pass
    
    def generate_content(self, prompt):
        try:
            genai.configure(api_key="AIzaSyBhppYwUZpoD8mqhnJ2ZLl1asuF957gFlU")  # Use environment variable or config file instead
            generation_config = {
                "temperature": 0.9,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }

            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ]

            model = genai.GenerativeModel(model_name="gemini-pro",
                                          generation_config=generation_config,
                                          safety_settings=safety_settings)

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
            return None

def main():

    result = ""
    answer_result = ""

    st.markdown("""
    <div style="text-align: center;">
    <h1>FJ Brainstorm Blitz</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center;">
    FJ Brainstorm Blitz is a dynamic application revolutionizing the creation of multiple-choice questions (MCQs), tailored to users' expertise and interests. By entering their area of expertise or preferred topic, users prompt the app to generate a customized set of MCQs. FJ Brainstorm Blitz not only facilitates quiz creation but also fosters learning through personalized suggestions based on user-generated questions and answers. With its user-friendly interface and AI-powered features, FJ Brainstorm Blitz aims to elevate learning experiences and promote knowledge acquisition across various disciplines and educational contexts.
    </div>
    """, unsafe_allow_html=True)

    info_generator = TestGenerator()

    if 'mcqs' not in st.session_state:
        st.session_state.mcqs = None

    topic_input = st.text_input("Enter your area of expertise or preferred topic:")

    if st.button("Generate MCQs") and topic_input:
        prompt = f"Generate 20 multiple-choice questions related to the topic: {topic_input} without answerkey"
        with st.spinner('Generating MCQs...'):
            st.session_state.mcqs = info_generator.generate_content(prompt)
        if st.session_state.mcqs:
            st.success("MCQs generated successfully!")
        else:
            st.error("Failed to generate MCQs.")

    if st.session_state.mcqs:
        st.subheader("Generated MCQs:")
        st.write(st.session_state.mcqs)

        collected_answers = []

        st.subheader("Enter Answers for the MCQs:")
        columns = st.columns(4)
        for i in range(20):
            with columns[i % 4]:
                answer_input = st.radio(f"Answer for MCQ {i+1}:", options=['A', 'B', 'C', 'D'])
                collected_answers.append(answer_input)

        if st.button("Generate Result"):
            # Create a DataFrame for collected answers
            collected_answers_df = pd.DataFrame({'Question': range(1, 21), 'Answer': collected_answers})
            collected_answers_df.index = collected_answers_df.index + 1

            with st.spinner('Generating Result...'):
                input_string = f"Provide the answer keys for the following questions related to {topic_input}: \n{st.session_state.mcqs} \nPlease provide the answers in capital letters (e.g., ABCD) in the format of a DataFrame."
                result = info_generator.generate_content(input_string)
                input_string2 = f"Match the answers provided by the user collected answer option{collected_answers_df}, is equal to the {result} generated answer option, and calculate the correct and incorrect answer if no answer match with the date its mean that all answers are incorrect"
                result2 = info_generator.generate_content(input_string2)
                input_string3 = f"please provide the sumrized result {result2}"
                result3 = info_generator.generate_content(input_string3)
            st.subheader("Generated Result:")
            st.write(result)
            st.write(result2)
            st.write(result3)
            

        if st.button("Generate Learning Suggestions"):
            with st.spinner('Generating Suggestions...'):
                suggestions_input = f"Based on the generated questions on the topic '{topic_input}' and the collected answers, here are some suggestions for further learning:"
                suggestions = info_generator.generate_content(suggestions_input)
                if suggestions:
                    st.subheader("Suggestions for Learning:")
                    st.write(suggestions)
                else:
                    st.error("Failed to generate suggestions.")

if __name__ == "__main__":
    main()
