import os
import shutil
import json
from langgraph.graph import StateGraph
from state import AgentState  
from agents.component_generate_agent import generate_ui_components
from agents.service_generate_agent import generate_services
from agents.page_generate_agent import generate_pages


graph = StateGraph(AgentState)


def clear_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)  
    os.makedirs(directory, exist_ok=True) 


def component_generate_node(state: AgentState) -> AgentState:
    clear_directory("angular-dashboard/src/app/components")
    srs_data = state.get("srs_data", {})

    
    if isinstance(srs_data, str):
        try:
            srs_data = json.loads(srs_data)
        except json.JSONDecodeError:
            print("❌ Error: Failed to parse srs_data JSON.")
            state["generated_components"] = {"error": "Invalid JSON format in SRS data."}
            return state

    ui_components = srs_data.get("uiComponents", [])
    if not ui_components:
        print("⚠️ Skipping component generation: No UI components found.")
        state["generated_components"] = {"error": "No UI components extracted from SRS."}
        return state

    structured_input = {
        "projectName": srs_data.get("projectName", "UnnamedProject"),
        "components": ui_components
    }

    print("🔹 Generating components with input:", structured_input)
    
    try:
        state["generated_components"] = generate_ui_components(structured_input)
    except Exception as e:
        print(f"❌ Component Generation Failed: {str(e)}")
        state["generated_components"] = {"error": str(e)}

    return state

graph.add_node("component_generate_node", component_generate_node)

def service_generate_node(state: AgentState) -> AgentState:
    clear_directory("angular-dashboard/src/app/services")
    srs_data = state.get("srs_data", {})

    
    if isinstance(srs_data, str):
        try:
            srs_data = json.loads(srs_data)
        except json.JSONDecodeError:
            print("❌ Error: Failed to parse srs_data JSON.")
            state["generated_services"] = {"error": "Invalid JSON format in SRS data."}
            return state

    services = srs_data.get("apiEndPoints", [])
    if not services:
        print("⚠️ Skipping service generation: No services found.")
        state["generated_services"] = {"error": "No services extracted from SRS."}
        return state

    structured_input = {
        "projectName": srs_data.get("projectName", "UnnamedProject"),
        "services": services
    }

    print("🔹 Generating services with input:", structured_input)
    
    try:
        state["generated_services"] = generate_services(structured_input)
    except Exception as e:
        print(f"❌ Service Generation Failed: {str(e)}")
        state["generated_services"] = {"error": str(e)}

    return state

graph.add_node("service_generate_node", service_generate_node)


def page_generate_node(state: AgentState) -> AgentState:
    clear_directory("angular-dashboard/src/app/pages")
    img_data = state.get("img_data", {})

    structured_input = {"img_data": img_data}

    print("🔹 Generating pages with input:", structured_input)

    try:
        state["generated_pages"] = generate_pages(structured_input)
    except Exception as e:
        print(f"❌ Page Generation Failed: {str(e)}")
        state["generated_pages"] = {"error": str(e)}

    return state

graph.add_node("page_generate_node", page_generate_node)


graph.set_entry_point("component_generate_node")
graph.add_edge("component_generate_node", "service_generate_node")
graph.add_edge("service_generate_node", "page_generate_node")


internal_codegen_graph = graph.compile()


class AutonomousCodeGenerator:
    def run(self, state: AgentState) -> AgentState:
        """Runs the internal LangGraph for code generation."""
        print("🚀 Starting Autonomous Code Generation...")

        internal_codegen_graph.get_graph().draw_mermaid_png(output_file_path="output/internal_codegen_graph.png")
        result = internal_codegen_graph.invoke(state)
        state.update(result)  

        self.setup_project()
        return state

    def setup_project(self):
        """Handles routing, state management, and app.component.html updates."""
        os.system("cd angular-dashboard && ng generate module app-routing --flat --module=app")
        os.system("cd angular-dashboard && npm install @ngrx/store @ngrx/effects")

        print("✅ Project setup completed with routing & state management.")