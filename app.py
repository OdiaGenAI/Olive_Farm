import streamlit as st
import requests
import justext
import pdfplumber
import docx2txt
import json
import ast
import os
import re
import openai
import json

from custom_prompt_template import InstructionGenerationTemplate, AnswerGenerationTemplate


st.set_page_config(page_title="LLM instruction Generator")

st.sidebar.success("Select a page above")


# function for the odia stoplists justext
def odia_stoplist():
    odia_stopwords = [
        "ଏହି", "ଏକ", "ଏକାଉଣଟ", "ମୁଁ", "ମୋର", "ମୁଁ ନିଜେ", "ଆମେ", "ଆମର", "ଆମର", "ଆମେ ନିଜେ", "ତୁମେ", "ତୁମର", "ତୁମର",
        "ନିଜେ", "ନିଜେ", "ସେ", "ତାଙ୍କୁ", "ତାଙ୍କର",
        "ନିଜେ", "ସେ", "ତାଙ୍କୁ", "ତାଙ୍କର", "ନିଜେ", "ଏହା", "ଏହାର", "ନିଜେ |", "ସେମାନେ", "ସେଗୁଡିକ", "ସେମାନଙ୍କର",
        "ସେମାନଙ୍କର", "ନିଜେ |", "କଣ", "ଯାହା", "କିଏ", "କାହାକୁ",
        "ଏହା", "ତାହା", "ଏଗୁଡ଼ିକ", "ସେଗୁଡ଼ିକ", "ମୁଁ", "ହେଉଛି", "ହେଉଛି |", "ଥିଲା", "ଥିଲା |", "ହୁଅ", "ହୋଇସାରିଛି |", "ହେବା",
        "ଅଛି", "ଅଛି", "ଥିଲା", "ଅଛି", "କର", "କରେ |",
        "କରିଛନ୍ତି", "କରିବା", "ଏବଂ", "କିନ୍ତୁ", "ଯଦି", "କିମ୍ବା", "କାରଣ", "ଯେପରି", "ପର୍ଯ୍ୟନ୍ତ", "ଯେତେବେଳେ", "ର", "ପାଇଁ",
        "ସହିତ", "ବିଷୟରେ", "ବିପକ୍ଷରେ", "ମଧ୍ୟରେ", "ଭିତରକୁ", "ମାଧ୍ୟମରେ",
        "ସମୟରେ", "ପୂର୍ବରୁ", "ପରେ", "ଉପରେ", "ନିମ୍ନରେ |", "କୁ", "ଠାରୁ", "ଅପ୍", "ତଳକୁ", "ଭିତରେ", "ବାହାରେ", "ଉପରେ", "ବନ୍ଦ",
        "ସମାପ୍ତ", "ତଳେ |", "ପୁନର୍ବାର", "ଆଗକୁ",
        "ତାପରେ", "ଥରେ |", "ଏଠାରେ", "ସେଠାରେ", "କେବେ", "କେଉଁଠାରେ", "କିପରି", "ସମସ୍ତ", "ଉଭୟ", "ପ୍ରତ୍ୟେକ", "ଅଳ୍ପ", "ଅଧିକ",
        "ଅଧିକାଂଶ", "ଅନ୍ୟ", "କେତେକ", "ଏହିପରି",
        "ନୁହେଁ |", "କେବଳ", "ନିଜର", "ସମାନ", "ତେଣୁ", "ଅପେକ୍ଷା", "ମଧ୍ୟ", "ବହୁତ", "କରିପାରିବେ |", "ଇଚ୍ଛା", "କେବଳ",
        "କରିବା ଉଚିତ", "ବର୍ତ୍ତମାନ"
    ]
    return frozenset(odia_stopwords)


# function to extract data from url using justext
def extract_data_from_url(url, language):
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            print("inside the response")
            response.raise_for_status()
            page = response.content
            para = ""
            if language == "English":
                paragraphs = justext.justext(page, justext.get_stoplist("English"))
            elif language == "Hindi":
                paragraphs = justext.justext(page, justext.get_stoplist("Hindi"), 70, 140, 0.0, 0.02, 0.5, 150, False)
            elif language == "Odia":
                paragraphs = justext.justext(
                    page, odia_stoplist(), 70, 140, 0.0, 0.02, 0.5, 150, False
                )

            for paragraph in paragraphs:
                if not paragraph.is_boilerplate:
                    para = para + "\n" + paragraph.text
            # returning the extracted data i.e para as string
            if para == "":
                st.error("Unable to extract data from the URL")
                return None
            else:
                return para
        else:
            st.error("Request failed ")
            return None
    except Exception as err:
        st.error(err)
        return None
        
    


# function to extract data from documents
def extract_data_from_documents(documents):
    data = ""
    if documents is not None:
        for document in documents:
            document_details = {
                "filename": document.name,
                "filetype": document.type,
                "filesize": document.size,
            }
            st.write(document_details)

            # Extract content from the txt file
            if document.type == "text/plain":
                # Read as bytes
                data += str(document.read(), "utf-8")

            # Extract content from the pdf file
            elif document.type == "application/pdf":
                # using pdfplumber
                try:
                    with pdfplumber.open(document) as pdf:
                        all_text = ""
                        for page in pdf.pages:
                            text = page.extract_text()
                            all_text += text + "\n"
                        data += all_text
                except requests.exceptions.RequestException as e:
                    st.write("None")

            # Extract content from the docx file
            elif (
                document.type
                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                data += docx2txt.process(document)

        # return extract data
        return data
    else:
        st.error("Error: An error occurred while fetching content.")
        # return extract status, and the data extracted
        return None


# function for the keyboard



# Check the inputs for language, promptType
def valid_drop_down(language, promptType, noOfQuestions, instructionFormat):
    langFlag = False
    promptFlag = False
    noOfQuestionFlag = False
    instructionFormatFlag = False

    if language:
        langFlag = True
    if promptType:
        promptFlag = True
    if noOfQuestions:
        noOfQuestionFlag = True
    if instructionFormat:
        instructionFormatFlag = True
    # checking for the compalsory inputs and return true only if all are set
    return langFlag & promptFlag & noOfQuestionFlag & instructionFormatFlag


def main():
    # setting up the initial session_states
    if "extract_button" not in st.session_state:
        st.session_state.extract_button = False
    if "submit" not in st.session_state:
        st.session_state.submit = False
    if "generated" not in st.session_state:
        st.session_state.generated = False
    if "selected" not in st.session_state:
        st.session_state.selected = False
    if "answered" not in st.session_state:
        st.session_state.answered = False

    st.subheader("LLM Instructions")

    # form to get the inputs
    with st.form(key="form1"):
        st.write("#")

        # dropdown for language
        language = st.selectbox("Select a language", ("", "English", "Hindi", "Odia"))

        # dropdown for prompt type
        promptType = st.selectbox(
            "Select the Prompt type", ("", "Input text", "Url", "Document")
        )
        # inputs for number
        noOfQuestions = st.number_input(
            "Number of questions to generate:", min_value=1, max_value=20, value=10
        )

        # dropdown for language
        instructionFormat = st.selectbox(
            "Format of instruction:", ("Imperative sentence", "Question")
        )

        # input text for openAiKey
        openAiKey = st.text_input(label="Input the openai key")
        if "openAiKey" in  st.session_state:
            st.session_state["openAiKey"]  = openAiKey
        else:
            st.session_state["openAiKey"]  = openAiKey

        st.write("##")

        # form submit button and setting up the session_state
        if st.form_submit_button():
            st.session_state.submit = True

    if st.session_state.submit:
        # extends the prompt form to extract the data
        with st.expander(label="prompt"):
            with st.form(key="form2"):
                # calling the function inside if to check valid drop down inputs
                if valid_drop_down(
                    language, promptType, noOfQuestions, instructionFormat
                ):
                    if promptType == "Input text":
                        inputText = st.text_area(
                            label="For Instructions",
                            placeholder="Please enter your text here",
                        )

                    elif promptType == "Url":
                        url = st.text_input(
                            label="For URL", placeholder="Please enter your text here"
                        )
                    elif promptType == "Document":
                        documents = st.file_uploader(
                            label="For Documents ( pdf / txt / docx )",
                            type=["pdf", "txt", "docx"],
                            accept_multiple_files=True,
                        )

                    # if addInfoCheckbox:
                    #     additionalInfo = st.text_input(
                    #         label="Additional Instructions",
                    #         placeholder="Please enter your text here",
                    #     )

                    if st.form_submit_button():
                        st.session_state.extract_button = True
                        # st.experimental_rerun()

    # extracting data
    if st.session_state.extract_button:
        # extracting data
        
        if promptType == "Input text":
            extractedData = inputText

        elif promptType == "Url":
            extractedURLData = extract_data_from_url(url, language)
            if extractedURLData is not None:
                extractedData = extractedURLData
                st.text_area("Extracted Text:", value=extractedData, height=200)
            else:
                extractedData = False
        elif promptType == "Document":
            if not documents:
                documents = None
            else:
                for doc in documents:
                    if doc.name.split(".")[-1].lower() not in ["pdf", "txt", "docx"]:
                        # if documents is not the relevant type
                        st.error("Unsupported file: " + doc.name)

                extractedDocumentData = extract_data_from_documents(documents)
                extractedData = extractedDocumentData


        # if the values are extracted running the custom prompt by creating an instance
        if extractedData:


            # -----------------------------    RUNNING THE PROMPT   -----------------------------
            if "extractedData" not in st.session_state:
                st.session_state["extractedData"] = extractedData
            else:
                st.session_state["extractedData"] = extractedData

            if "Initial" not in st.session_state:
                st.session_state.Initial=True

            if st.session_state.Initial == True:
                
                # running the prompt form here

                openai.api_key = st.session_state["openAiKey"]
                my_prompt_template = InstructionGenerationTemplate()

                # providing the rules for the instructions to be generated
                additional_rules = """
                - You do not need to provide a response to the generated examples.
                - You must return the response in the specified language.
                - Each generated instruction can be either an imperative sentence or a question.
                """

                if st.button("Generate Instructions"):
                    prompt = my_prompt_template.format(
                        num_questions=noOfQuestions, 
                        context=extractedData, 
                        instruction_format=instructionFormat, 
                        lang=language, 
                        additional_rules=additional_rules
                    )
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                                {"role": "system", "content": prompt},
                            ])
                # if st.button("Generate Instructions"):
                    print("Generate button")
                    print("Checkpoint 1!")
                    
                    if "result" not in st.session_state:
                        content = response.choices[0].message.content
                        # content = "\n1. helloworld1.\n2. helloworld2"
                        responses_list = content.split('\n')
                        responses_list = [re.sub(r'^\s*\d+\.\s*', '', resp) for resp in responses_list if resp]
                        st.session_state["result"]=responses_list
                        st.session_state.generated = True
                    st.session_state.Initial = False
            if st.session_state.generated:
                # displaying the generated instructions
                st.write("Generated Insuctions")
                result = st.session_state["result"]
                # print(type(result))
                # print(result)
                result_dict = {i+1: value for i,value in enumerate(result)}
                selected_items = [f" {value} " for key, value in result_dict.items() if st.checkbox(f"Q{key} : {value}")]
                # print(type(result_dict))
                # print(result_dict)
                print("Checked point 2!")
                # Display the selected items as a list
                if selected_items:
                    st.write("Selected Items:")
                    st.write(selected_items)
                    if "selected_items" not in st.session_state:
                        st.session_state["selected_items"] = selected_items
                    st.session_state["selected_items"] = selected_items
                    st.session_state.selected = True
                else:
                    st.write("No items selected.")
            


            # -----------------------------    RUNNING THE PROMPT FOR ANSWER GENERATION  -----------------------------
            
           

            if st.session_state.selected:

                if "Initial2" not in st.session_state:
                    st.session_state.Initial2=True
            
                if st.session_state.Initial2:
                    # running the prompt form here
                    openai.api_key = st.session_state["openAiKey"]
                    my_prompt_template2 = AnswerGenerationTemplate()

                     # providing the rules for the answers to be generated
                    additional_rules = """
                        Enumerate the answers and dont provide any additional tags.
                    """
                   
                    question =  st.session_state["selected_items"]
                    if st.button("Generate Answers"):
                        prompt = my_prompt_template2.format(
                               questions=question,
                               additional_rules = additional_rules
                        )
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                    {"role": "system", "content": prompt},
                                ])

                    # if st.button("Generate Answers"):
                        # print("\n\n\n\nInside Answersss:\n\n\n\n")
                        # print(st.session_state["selected_items"])
                        
                        # print("Generate button")
                        # print("Checkpoint 3!")

                        if "answers" not in st.session_state:
                            content = response.choices[0].message.content
                            # content = "\n1. Answer1.\n2. Answer2"
                            print("\n\n\n\n\nAnswerss before regex\n\n\n\n")
                            print(content)
                            # print("Answer Type:" + str(type(content)))
                            responses_list = content.split('\n')
                            # print("\n\n\n\n\nAnswerss before regex after splitting\n\n\n\n")
                            # print(responses_list)
                            # print("Answer Type:" + str(type(responses_list)))

                            responses_list = [re.sub(r'^\s*\d+\.\s*', '', resp) for resp in responses_list if resp]
                            st.session_state["answers"]=responses_list
                            st.session_state.answered = True
                        st.session_state.Initial2 = False
                
                if st.session_state.answered:
                    # displaying the generated Answers
                    
                    questions = st.session_state["selected_items"]
                    answers = st.session_state["answers"]
                    # print("\n\n\n\n\nAnswerss after regex\n\n\n\n")
                    # print(answers)
                    # print("Answer Type:" + str(type(answers)))
                    answers_dict = {i+1: value for i,value in enumerate(answers)}
                    # print(type(answers_dict))
                    # print(answers_dict)
                    # print("Checked point 4!")
                    # st.write("answers")
                    st.write(answers_dict)

                    # Create a list to hold the JSON-like data
                    st.write("Generated Questions and Answers")
                    # Create a list of dictionaries
                    jsonl_data = [{"Question": question, "Answer": answers_dict.get(i, 'No answer found')} for i, question in enumerate(questions, start=1)]
                    
                
                    st.write(jsonl_data)
                    jsonl_string = '\n'.join(json.dumps(item, ensure_ascii=False) for item in jsonl_data)

                    # Display the JSONL data
                    print(jsonl_string)

                    if st.download_button(label="Save as jsonl", data=jsonl_string, mime="application/json"):
                        st.success("Successfully saved")


                    
                
        if st.button("Clear"):
            st.session_state.extract_button = False
            st.session_state.submit = False
            st.session_state.generated = False
            st.session_state.selected = False
            st.session_state.answered = False
            

            
            if "Initial" in st.session_state:
                st.session_state.Initial = True
            if "Initial2" in st.session_state:
                st.session_state.Initial2 = True


            if "openAiKey" in  st.session_state:
                del st.session_state["openAiKey"]
            if "extractedData" in st.session_state:
                del st.session_state["extractedData"]
            if "result" in  st.session_state:
                del st.session_state["result"]  
            if "selected_items" in  st.session_state:
                del st.session_state["selected_items"]  
            if "answered" in  st.session_state:
                del st.session_state["answers"]  
            st.experimental_rerun()


if __name__ == "__main__":
    main()
