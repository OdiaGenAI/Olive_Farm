import openai
import streamlit as st
from camel.agents import RolePlaying
from camel.utils import print_text_animated
from datetime import datetime



def task_generator(user,assistant, openAiKey):
    
    openai.api_key = openAiKey

    prompt = f'''User: Farmer, Assistant: Business analyst
    Generate a conversation topic: Help the farmer in deciding the optimal choice for crops this year\n
    User: Accountant, Assistant: Developer
    Generate a conversation topic: Developing a custom accounting software to automate financial processes and reduce errors.\n
    User: Athlete, Assistant: Doctor
    Generate a conversation topic: Developing a personalized nutrition plan to optimize athletic performance and recovery.\n
    User: Politician, Assistant: Social Media Manager\n
    Generate a conversation topic: Develop a social media strategy to increase the politician's online presence and engagement with constituents.\n
    User: {user}, Assistant: {assistant}
    Generate a conversation topic:'''

    response = openai.Completion.create(
    engine="text-davinci-002", #Use gpt-3 engine.
    prompt=prompt,
    max_tokens=50,
    n=1
    )
    task = response.choices[0].text.strip()

    return task

def conversation_generator(user,assistant, task, chat_limit=2):
    task_prompt = task
    print(task)
    print(user)
    print(assistant)
    role_play_session = RolePlaying(assistant, user, task_prompt)
    # print(Fore.CYAN + f"Specified task prompt:\n{role_play_session.task_prompt}\n")
    # print(f"Specified task prompt:\n{role_play_session.task_prompt}\n")

    chat_turn_limit, n = chat_limit, 0
    assistant_msg, _ = role_play_session.init_chat()

    user_chat = []
    assistant_chat = []
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    while n < chat_turn_limit:
        n += 1
        try:
            (assistant_msg, _, _), (user_msg, _, _) = role_play_session.step(assistant_msg)
            assert user_msg.content is not None
            with st.chat_message("user"):
                user_content = user_msg.content.replace("Instruction: ", "").replace("Input: None", "")
                st.text(user_content)
            assert assistant_msg.content is not None
            with st.chat_message("assistant"):
                assistant_content = assistant_msg.content.replace("Solution: ", "").replace("Next request.","")
                st.text(assistant_content)
            
        except:
            break

        # print(Fore.BLUE + f"AI User:\n\n{user_msg.content}\n\n")
        # print(f"AI User:\n\n{user_msg.content}\n\n")
        user_chat.append(user_msg.content)
        if "Next request." not in assistant_msg.content:
            break

        # print(Fore.GREEN + f"AI Assistant:\n\n{assistant_msg.content}\n\n")
        # print(f"AI Assistant:\n\n{assistant_msg.content}\n\n")
        assistant_chat.append(assistant_msg.content)
        if "<CAMEL_TASK_DONE>" in user_msg.content:
            break

    #Processing the generated conversation

    final_user_convo = []
    final_assistant_convo = []

    if len(assistant_chat)==0 or len(user_chat)==0:
        return "Empty list"


    for i in range(len(user_chat)):

        if ("Next request" in assistant_chat[i]) and ("Instruction:" in user_chat[i]) and ("Input:" in user_chat[i]):
            final_instruction = ""
            try:
                instruction = user_chat[i].split("Instruction:")[1].split("Input:")[0]
                input = user_chat[i].split("Input:")[1].strip()
            except:
                continue

            if input.strip() == 'None':
                final_instruction = final_instruction+instruction.replace("\n"," ")
                final_instruction = final_instruction.strip()
            else:
                final_instruction = instruction.replace("\n"," ")+"\ninput:"+input #If an input is there, then add a newline after instruction, input: and then the input.
                final_instruction = final_instruction.strip()

            final_user_convo.append(final_instruction)
            final_assistant_convo.append(assistant_chat[i].replace("Solution:","").replace("Next request.","").strip())

        else:
            break #Sometimes faulty chat gets generated. A proper convo has Next request at the end

    assert (len(final_user_convo)-len(assistant_chat))<=1
    # print('\n\n'+'End of the conversation\n\n')
    # print("*"*150, end='\n')
    final_convo_list = []

    for i in range(len(final_user_convo)):
        user_convo = {"from":"user","value":final_user_convo[i]}
        assistant_convo = {"from":"assistant","value":final_assistant_convo[i]}
        final_convo_list.append(user_convo)
        final_convo_list.append(assistant_convo)

    length = len(final_convo_list)

    final_json_entry = {'user':user,'assistant':assistant,'task':task_prompt,'conversations':final_convo_list, 'specified_task':role_play_session.task_prompt, 'length':length}
    # pprint.pprint(final_json_entry)
    return final_json_entry, final_user_convo, final_assistant_convo