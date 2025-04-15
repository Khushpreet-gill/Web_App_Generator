from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from retriever import retrieve_context
import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda

load_dotenv(override=True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY,temperature=0.2)

prompt = PromptTemplate(
    input_variables=["context"],
    template="Based on the following context, process user query to generate python code:\n{context}"
)

agent_chain = RunnableLambda(lambda x: llm.invoke(prompt.format(context=x)))

def generate_agent(context):
    """Generate agent code based on retrieved context."""
    return agent_chain.invoke(context)  

def save_agent_to_file(agent_code, filename="new_agent.py"):
    """Save the generated agent code to a file."""
    
    if not isinstance(agent_code, str):
        agent_code = str(agent_code)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(agent_code)
    
    print(f"\nAgent code successfully written to {filename}")


if __name__ == "__main__":
    query = input("Enter query: ")
    context = retrieve_context(query) 

    if context == "No relevant context found. Try re-ingesting documents.":
        print("No relevant context available. Please re-ingest documents.")
    else:
        agent_code = generate_agent(context)
        print("\nGenerated Agent Code:\n", agent_code)

        
        save_agent_to_file(agent_code)

        # os.system(f"python {filename}")
