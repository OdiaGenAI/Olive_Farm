import openai
import os
import streamlit as st
from custom_prompt_template import InstructionGenerationTemplate
openai.api_key = os.getenv("OPENAI_API_KEY")
my_prompt_template = InstructionGenerationTemplate()
st.title("Instruction generation using GPT-3.5")
num_questions = st.number_input("Number of questions to generate:", min_value=1, max_value=20, value=10)
context=st.text_area("Enter the context on which you want to build instructions")
instruction_format = st.selectbox("Format of instruction:", ["Imperative sentence", "Question"])
lang=st.selectbox("Select language for the response:",["English","Hindi","Odia"])
additional_rules = """
- You do not need to provide a response to the generated examples.
- You must return the response in the specified language.
- Each example must include an instruction.
- Each generated instruction can be either an imperative sentence or a question.
- Each example must start with the label "<example>" and end with the label "</example>".
"""

if st.button("Generate"):
    prompt = my_prompt_template.format(
        num_questions=num_questions, 
        context=context, 
        instruction_format=instruction_format, 
        lang=lang, 
        additional_rules=additional_rules
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": prompt},
                # {"role": "user", "content": f"Generate {num_questions} diverse questions based on the context provided below in the form of {instruction_format}.\n\n{context}\n\n{additional_rules}"},
            ])


    result = response.choices[0].message.content
    # for choice in response.choices:
    #     result += choice.message.content
    examples = result.split("<example>")
# Remove empty strings from the list and strip end tags
    examples = [ex.replace("</example>", "").strip() for ex in examples if ex]

# Create a new list with numbered examples
    numbered_examples = [f"{i+1}. <example>{ex}</example>" for i, ex in enumerate(examples)]

# Join the numbered examples with newline characters to create a single string
    formatted_result = "\n".join(numbered_examples)



    st.write("Generated Questions:")
    st.write(formatted_result)
