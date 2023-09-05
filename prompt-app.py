import openai
import os
import streamlit as st
openai.api_key = os.getenv("OPENAI_API_KEY")


st.title("Instruction generation using GPT-3.5")

num_questions = st.number_input("Number of questions to generate:", min_value=1, max_value=20, value=10)
context=st.text_area("Enter the context on which you want to build instructions")
instruction_format = st.selectbox("Format of instruction:", ["Imperative sentence", "Question"])
lang=st.selectbox("Select language for the response:",["English","Hindi"])
additional_rules = f"""You do not need to provide a response to the generated examples.
you must return the response in {lang}.
Each example must include an instruction.
Each generated instruction can be either an imperative sentence or a question.
Each example must start with the label \"<example>\" and end with the label \"</example>\""""

if st.button("Generate"):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a chatbot generate response as per intructions"},
                {"role": "user", "content": f"Generate {num_questions} diverse questions based on the context provided below in the form of {instruction_format}.\n\n{context}\n\n{additional_rules}"},
            ])


    result = ''
    for choice in response.choices:
        result += choice.message.content


    st.write("Generated Questions:")
    st.write(result)
