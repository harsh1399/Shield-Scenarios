# Step 1: Import All the Required Libraries

# We are creating a Webapp with Streamlit
import streamlit as st
import requests
import json
import Maps
import pygame
import os



# Step 2: Add a title to your Streamlit Application on Browser

st.set_page_config(page_title="🦙💬 Mistral Chatbot with Streamlit")
json_config = None

#Create a Side bar
with st.sidebar:
    st.title("🦙💬 Shield AI Chatbot")
    # st.header("Settings")
    #
    # add_replicate_api=st.text_input('Enter the Replicate API token', type='password')
    # if not (add_replicate_api.startswith('r8_') and len(add_replicate_api)==40):
    #     st.warning('Please enter your credentials', icon='⚠️')
    # else:
    #     st.success('Proceed to entering your prompt message!', icon='👉')
    #
    # st.subheader("Models and Parameters")
    #
    # select_model=st.selectbox("Choose a Llama 2 Model", ['Llama 2 7b', 'Llama 2 13b', 'Llama 2 70b'], key='select_model')
    # if select_model=='Llama 2 7b':
    #     llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    # elif select_model=='Llama 2 13b':
    #     llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    # else:
    #     llm = 'replicate/llama70b-v2-chat:e951f18578850b652510200860fc4ea62b3b16fac280f83ff32282f87bbd2e48'
    #
    # temperature=st.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    # top_p=st.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    # max_length=st.slider('max_length', min_value=64, max_value=4096, value=512, step=8)
    #
    # st.markdown('I make content on AI on regular basis do check my Youtube channel [link](https://www.youtube.com/@muhammadmoinfaisal/videos)')

# os.environ['REPLICATE_API_TOKEN']=add_replicate_api
#
# #Store the LLM Generated Reponese
#
if "messages" not in st.session_state.keys():
    st.session_state.messages=[{"role": "assistant", "content":"How may I assist you today?"}]

# # Diplay the chat messages

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# # Clear the Chat Messages
def clear_chat_history():
    st.session_state.messages=[{"role":"assistant", "content": "How may I assist you today"}]

def show_map():
    width = 1260
    height = 720
    with open('Data/configuration.json', 'w') as f:
        f.write(json_config)

    Maps.create_map_from_json("Data/configuration.json")
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    Maps.initMaps(screen, (width, height), 25, 100)
    newMap = Maps.Maps()
    newMap.showMap([0, "custom"])
    Maps.close_pygame()
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def execute_config():
    width = 1260
    height = 720
    Maps.create_map_from_json("Data/configuration.json")
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    Maps.initMaps(screen, (width, height), 25, 100)
    newMap = Maps.Maps()
    shooters_behavior = Maps.get_behavior_from_json("shooters")
    tanks_behavior = Maps.get_behavior_from_json("tanks")
    helicopters_behavior = Maps.get_behavior_from_json("helicopters")
    positions = Maps.troops_positions()
    newMap.openMap([0, "custom", shooters_behavior, tanks_behavior, helicopters_behavior, positions])
    Maps.close_pygame()

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
st.sidebar.button('Show Map', on_click = show_map)
st.sidebar.button('Execute configuration',on_click = execute_config)
# # Create a Function to generate the Llama 2 Response
def generate_response(prompt_input):
    # default_system_prompt="You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    # for data in st.session_state.messages:
    #     # print("Data:", data)
    #     if data["role"]=="user":
    #         default_system_prompt+="User: " + data["content"] + "\n\n"
    #     else:
    #         default_system_prompt+="Assistant" + data["content"] + "\n\n"
    # print(prompt_input)
    # config_prompt = HumanMessagePromptTemplate.from_template(
    #     "Generate the JSON according to the information given in the question. Follow the format specified in the formatting instructions. \nJson Formatting instructions:\n{format_instructions}\n question:\n{question}"
    # )
    # print(parser.get_format_instructions())
    # if prompt_input[:4] == "INST":
    #     human_msg = config_prompt.format(format_instructions=parser.get_format_instructions(),
    #                                 question=prompt_input[6:]).content
    # else:
    #     human_msg = prompt_input
    # print(human_msg)
    response = requests.post(
        "https://cc73-155-98-12-76.ngrok-free.app/configure_json/invoke",
        json={'input': {
            "human_input":  f'{prompt_input}'}}
    )
    # print(response.content)
    # config = json.loads(response.json()['output']['content'])
    #
    # with open('Data/configuration.json', 'w') as f:
    #     json.dump(config, f)

    # output=replicate.run(llm, input={"prompt": f"{default_system_prompt} {prompt_input} Assistant: ",
    #                                  "temperature": temperature, "top_p":top_p, "max_length": max_length, "repititon_penalty":1})

    return response.content


#User -Provided Prompt

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content":prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a New Response if the last message is not from the asssistant

if st.session_state.messages[-1]["role"] != "assistant":
    original_response = ""
    with st.chat_message("assistant"):
        with st.spinner("Generating..."):
            original_response=generate_response(prompt)
            json_output = json.loads(original_response.decode('ascii'))
            response = json.loads(json_output['output'])
            json_config = json.dumps(response,indent=4)
            placeholder=st.empty()
            # print(response.decode('ascii')['output'])
            # full_response=''
            # for item in response:
            #     full_response+=item
            #     placeholder.markdown(full_response)
            placeholder.markdown(st.json(response))

    message= {"role":"assistant", "content":original_response}
    st.session_state.messages.append(message)




