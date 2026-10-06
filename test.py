from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph_tools import all_tools

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.4)

llm_with_tools = llm.bind_tools(all_tools)

result = llm_with_tools.invoke("What is current temperature in New York City?")

print(result)