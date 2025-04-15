import os
import json
from langchain.tools import tool
from groq import Groq
from langchain_core.runnables.graph_mermaid import draw_mermaid_png


# Initialize LLM
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-key")
ai_client = Groq(api_key=GROQ_API_KEY)


def generate_workflow_diagram():
    """Generates a Mermaid diagram of the LangGraph workflow."""

    from workflow import workflow

    workflow.get_graph().draw_mermaid_png(output_file_path="output/my.png")
    print("✅ LangGraph workflow diagram saved!")

# Function to generate README.md
def generate_readme(state):
    """Uses LLM to generate project documentation."""
    from state import AgentState

    project_name = getattr(state, "srs_data", {}).get("projectName", "Angular Project")
    components = getattr(state, "generated_components", {})
    services = getattr(state, "generated_services", {})
    pages = getattr(state, "generated_pages", {})

    prompt = f"""
    Generate a README.md for the project "{project_name}" with:
    1. Setup Instructions (clone, install dependencies, run)
    2. Usage Guide (project features, navigation)
    3. Project Structure (folders, key files)
    4. List of components: {list(components)}
    5. List of services: {list(services)}
    6. List of pages: {list(pages)}

    Return the full README.md content.
    """

    response = ai_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        readme_content = response.choices[0].message.content
        os.makedirs("docs", exist_ok=True)
        with open("docs/README.md", "w", encoding="utf-8") as file:
            file.write(readme_content)
        print("✅ README.md generated successfully!")
    except Exception as e:
        print(f"❌ Failed to generate README.md: {str(e)}")

# Function to generate component documentation
# def generate_component_docs(state):
#     """Uses LLM to generate detailed documentation for components."""

#     components = getattr(state, "generated_components", {})
#     if not components:
#         print("⚠️ No components found, skipping component docs.")
#         return

#     component_docs = {}
#     for component in components:
#         prompt = f"""
#         Generate detailed documentation for the Angular component "{component}".
#         Include:
#         - Props (inputs/outputs)
#         - State management
#         - API integrations (if any)
#         - Usage examples
#         """

#         response = ai_client.chat.completions.create(
#             model="llama-3.2-11b-vision-preview",
#             messages=[{"role": "user", "content": prompt}],
#         )

#         try:
#             doc_content = response.choices[0].message.content
#             component_docs[component] = doc_content
#             os.makedirs("docs/components", exist_ok=True)
#             with open(f"docs/components/{component}.md", "w", encoding="utf-8") as file:
#                 file.write(doc_content)
#             print(f"✅ Documentation created for {component}")
#         except Exception as e:
#             print(f"❌ Failed to generate docs for {component}: {str(e)}")

# Main function for the documentation agent
def documentation_agent(state):
    """Runs the documentation generation process."""
    generate_workflow_diagram()
    generate_readme(state)
    # generate_component_docs(state)
    # state["documentation_status"] = "Documentation generated successfully"
    return state