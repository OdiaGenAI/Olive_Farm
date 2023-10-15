import streamlit as st
from user_roles import user_role_list
from promptTemplate import task_generator
from promptTemplate import conversation_generator
import openai
import json



# page title
st.set_page_config(page_title="LLM Roleplay")

# sidebar content
with st.sidebar:
    st.markdown("My side bar")

# main function
def main():
    st.title("LLM Roleplay")

    if "submit" not in st.session_state:
        st.session_state.submit = False
    if "submit2" not in st.session_state:
        st.session_state.submit2 = False
    if "initial" not in st.session_state:
        st.session_state.initial = False
    if "initial2" not in st.session_state:
        st.session_state.initial2 = False
    if "extracted" not in st.session_state:
        st.session_state.extracted = False

    with st.form(key="form"):
        role1, role2 = st.columns([0.5, 0.5])

        with role1:
            # role selection dropdown menu
            selected_roles_user = st.multiselect("Select User Roles", user_role_list)
            user = ', '.join(selected_roles_user)
            # user = st.text_input("User Role (EDIT ME)", value=', '.join(selected_roles_user))

        with role2:
            # role selection dropdown menu
            selected_roles_assistant = st.multiselect("Select Assistant Roles", user_role_list)
            assistant = ', '.join(selected_roles_assistant)
            # assistant = st.text_input("Assistant Role (EDIT ME)", value=', '.join(selected_roles_assistant))

        # input for chat_limit
        chat_limit = st.number_input(
            "Messages to generate:", min_value=1, max_value=20, value=5
        )

         # input text for openAiKey
        openAiKey = st.text_input(label="Input the openai key", type="password")

        # form submit button and setting up the session_state
        if st.form_submit_button(label="Submit"):
            st.session_state.submit = True
            st.session_state.initial = True
            # print(user)
            # print(assistant)
            # print(prompt(user, assistant))

    if st.session_state.submit:
        print("Inside submit")
        with st.spinner("In progress..."):
            try:
                if st.session_state.initial:
                    st.session_state["task"] = task_generator(user, assistant, openAiKey)
                    print("task_generator")
                    # print("\n\n\nAfter the task\n\n\n")
                    st.session_state.initial = False
                with st.form(key="form2"):

                    # input text for task
                    st.session_state["task"] = st.text_input("The topic for the roleplay (Edit if required)", value=st.session_state["task"])

                    if st.form_submit_button(label="Generate"):
                        st.session_state.submit2 = True
                        # print(st.session_state["task"])
                        st.session_state.initial2 = True
                        # print("\n\nsubmit2 statues:")
                        # print(st.session_state.submit2)
                        # print("\n\n")
            except Exception as err:
                st.error(err)
                
                
            

    if st.session_state.submit2:
        print("Inside submit2")
        st.session_state.extracted = False
        with st.expander(label="role play"):
            with st.spinner("Generating..."):
                try:
                    if st.session_state.initial2:
                        
                        roleplay, user_convo, assistant_convo = conversation_generator(user, assistant, st.session_state["task"],chat_limit)
                        # roleplay = {'user': 'Actor', 'assistant': 'Chef', 'task': "Planning and preparing healthy meals that meet the actor's strict dietary requirements.", 'conversations': [{'from': 'user', 'value': 'Create a list of movie genres that will inspire each course of the menu.'}, {'from': 'assistant', 'value': 'To create a list of movie genres that will inspire each course of the menu, we can consider a variety of genres that offer distinct flavors and themes. Here is a suggested list:\n\n1. Sci-Fi: Molecular Gastronomy Appetizer\n2. Romance: Elegant Seafood Entrée\n3. Action: Spicy Asian Fusion Main Course\n4. Comedy: Playful Dessert\n5. Western: Smoked BBQ Main Course'}, {'from': 'user', 'value': 'Choose a specific sci-fi movie that will inspire the molecular gastronomy appetizer.'}, {'from': 'assistant', 'value': 'To choose a specific sci-fi movie that will inspire the molecular gastronomy appetizer, we can look for a movie that showcases futuristic technology, innovative concepts, and unique visuals. One movie that fits this description is "Blade Runner." The dystopian setting and advanced technology in the movie can serve as inspiration for creating a visually stunning and futuristic molecular gastronomy appetizer.'}], 'specified_task': 'Chef will help Actor create a delectable five-course menu inspired by movie genres. From a sci-fi-inspired molecular gastronomy appetizer to a western-themed smoked BBQ main course, Chef will bring the flavors and ambiance of each genre to life, ensuring a memorable dining experience for Actor and their guests.', 'length': 4}
                        st.session_state["roleplay"] = roleplay
                        st.session_state.initial2 = False
                        print("conversation_generator")
                        # print("roleplay")
                        # print(roleplay)
                        # print("user_convo")
                        # print(user_convo)
                        # print("assistant_convo")
                        # print(assistant_convo)
                    st.session_state.extracted = True
                except Exception as err:
                        st.error(err)
    
    if st.session_state.extracted:
        json_data = st.session_state["roleplay"]
        json_string = json.dumps(json_data, ensure_ascii=False)
        if st.download_button(label="Save as jsonl", data=json_string , mime="application/json"):
            st.success("Successfully saved")

        if st.button("Clear"):
            st.session_state.submit = False
            st.session_state.submit2 = False
            st.session_state.initial = False
            st.session_state.initial2 = False
            st.session_state.extracted = False
            if "task" in  st.session_state:
                del st.session_state["task"]
            if "roleplay" in st.session_state:
                del st.session_state["roleplay"]
            st.experimental_rerun()


if __name__ == "__main__":
    main()