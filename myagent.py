from langchain_community.tools.tavily_search import TavilySearchResults
import os

from package.common import read_api_key


# Define the environment variable
os.environ['TAVILY_API_KEY'] = read_api_key("TAVILY_API_KEY")

search = TavilySearchResults(
   
)
print(search.invoke("what is the weather in Almaty"))
      
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

loader = WebBaseLoader("https://docs.smith.langchain.com/")
docs = loader.load()
documents = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200
).split_documents(docs)
vector = FAISS.from_documents(documents, OpenAIEmbeddings())
retriever = vector.as_retriever()
print(retriever.get_relevant_documents("how to log a trace")[0])

from langchain.tools.retriever import create_retriever_tool

retriever_tool = create_retriever_tool(
    retriever,
    "langsmith_search",
    "Search for information about LangSmith. For any questions about LangSmith, you must use this tool!",
)

tools = [search, retriever_tool]

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

from langchain import hub

# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/openai-functions-agent")


from langchain.agents import create_openai_functions_agent

agent = create_openai_functions_agent(llm, tools, prompt)

from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print(agent_executor.invoke({"input": "hi!"}))