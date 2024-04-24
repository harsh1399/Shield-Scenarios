
from fastapi import FastAPI
from langserve import add_routes
# from llm_code import prompt,generate_response,conversation_buff_llm
# from langchain.chat_models import ChatAnthropic, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from Llama_cpp_gpu import conversation_buff_llm
# /home/default/workspace/venv/lib/python3.10/site-packages/chainlit

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

add_routes(app,RunnableLambda(conversation_buff_llm),path="/configure_json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)