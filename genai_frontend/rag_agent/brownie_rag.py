import os
import uuid
import chromadb
import pypdf
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph
from langgraph.pregel import END
from typing import TypedDict, Optional, Annotated
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import logging

# os.environ["GROQ_API_KEY"] = ""
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
knowledge_collection = chroma_client.get_or_create_collection(name="agent_knowledge")

text_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

agent_llm = ChatGroq(model="llama3-8b-8192", api_key="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", temperature=0.2)

app = FastAPI()

class AgentStateModel(TypedDict):
    user_prompt: str
    relevant_knowledge: Optional[Annotated[str, "relevant_knowledge"]]
    agent_blueprint: Optional[Annotated[str, "agent_blueprint"]]

def extract_text_from_pdf(pdf_file):
    document_text = ""
    pdf_reader = pypdf.PdfReader(pdf_file)
    for page in pdf_reader.pages:
        document_text += page.extract_text()
    return document_text

def split_text_into_segments(raw_text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    text_segments = text_splitter.split_text(raw_text)
    return text_segments

def fetch_contextual_information(state: AgentStateModel) -> AgentStateModel:
    user_query = state["user_prompt"]
    query_embedding = text_embedding_model.encode([user_query]).tolist()
    search_results = knowledge_collection.query(query_embeddings=query_embedding, n_results=5)

    retrieved_knowledge = search_results["documents"][0] if search_results["documents"] else []
    state["relevant_knowledge"] = (
        "\n\n".join(retrieved_knowledge)
        if retrieved_knowledge
        else "No relevant knowledge found."
    )
    return state

def create_agent_design(state: AgentStateModel) -> AgentStateModel:
    user_query = state["user_prompt"]
    knowledge_context = state["relevant_knowledge"]

    design_prompt = ChatPromptTemplate.from_template(
        """Given the following context, create a detailed and precise summary that answers the user's query.
        Context: {knowledge_context}
        User Query: {user_query}
        Summary:"""
    )
    messages = design_prompt.format_messages(user_query=user_query, knowledge_context=knowledge_context)

    try:
        agent_response = agent_llm.invoke(messages)
        state["agent_blueprint"] = agent_response.content.strip()
    except Exception as e:
        state["agent_blueprint"] = f"Error: Unable to generate summary. {e}"
    return state

agent_state_graph = StateGraph(AgentStateModel)
agent_state_graph.add_node("fetch_contextual_information", fetch_contextual_information)
agent_state_graph.add_node("create_agent_design", create_agent_design)

agent_state_graph.set_entry_point("fetch_contextual_information")
agent_state_graph.add_edge("fetch_contextual_information", "create_agent_design")
agent_state_graph.add_edge("create_agent_design", END)

agent_executor = agent_state_graph.compile()

def generate_ai_agent(query: str):
    agent_result = agent_executor.invoke({"user_prompt": query})
    return agent_result

@app.post("/upload_knowledge/")
async def upload_knowledge(files: List[UploadFile] = File(...)):
    for file in files:
        document_file = file.file
        document_text = extract_text_from_pdf(document_file)
        text_segments = split_text_into_segments(document_text)
        for segment in text_segments:
            segment_id = str(uuid.uuid4())
            knowledge_collection.add(documents=[segment], ids=[segment_id])
    return JSONResponse(content={"message": "Knowledge base updated successfully"})

@app.post("/create_agent/")
async def create_ai_agent_endpoint(query: str, agent_name: str = Query(...)):
    agent_design = generate_ai_agent(query)
    agent_details = agent_design['agent_blueprint']

    code_generation_prompt = ChatPromptTemplate.from_template(
        """Based on the provided information, generate well-structured and functional Python code for an AI agent.
        Don't give any form of comments, description, header, footer. Only give the code.
        Information: {agent_details}
        Agent Name: {agent_name}
        Code: (Strictly no comments)""" 
    )

    messages = code_generation_prompt.format_messages(agent_details=agent_details, agent_name=agent_name)

    try:
        agent_code = agent_llm.invoke(messages).content.strip()
        file_path = f"{agent_name}.py"
        with open(file_path, "w") as f:
            f.write(agent_code)
        return JSONResponse(content={"message": f"Agent '{agent_name}.py' created successfully"})
    except Exception as e:
        # logger.error(f"Error creating agent: {e}")
        return JSONResponse(content={"error": f"Error creating agent: {e}"})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
