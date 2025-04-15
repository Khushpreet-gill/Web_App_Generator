from langgraph.graph import StateGraph
from state import AgentState  
import json
#Import Autonomous Code Generator
from agents.code_generator import AutonomousCodeGenerator
from agents.test_debug_agent import generate_ui_tests, run_cypress_tests, debug_failing_components
from agents.docker_generate_agent import generate_dockerfile
from agents.documentation_agent import documentation_agent

graph = StateGraph(AgentState)

def srs_node(state: AgentState) -> AgentState:
    from agents.srs_agent import process_srs  
    srs_data = process_srs(state["srs_path"])
    state["srs_data"] = srs_data
    return state
graph.add_node("srs_node", srs_node)

def img_node(state: AgentState) -> AgentState:
    from agents.img_agent import process_image  
    img_data = process_image(state["img_path"])
    state["img_data"] = img_data
    return state
graph.add_node("img_node", img_node)

def project_setup_node(state: AgentState) -> AgentState:
    from agents.project_setup_agent import GenerateProjectSetupAgent  
    project_agent = GenerateProjectSetupAgent()
    state = project_agent.run(state)
    return state
graph.add_node("project_setup_node", project_setup_node)

def autonomous_code_generator_node(state: AgentState) -> AgentState:
    """Runs Autonomous Code Generation for Components, Services, and Pages."""
    code_generator = AutonomousCodeGenerator()
    
    state = code_generator.run(state)
    
    state["code_generation_status"] = "Completed"
    return state

graph.add_node("autonomous_code_generator_node", autonomous_code_generator_node)

def testing_debugging_node(state: AgentState) -> AgentState:
    from agents.test_debug_agent import generate_ui_tests, run_cypress_tests  

    print("🔍 Debugging: Running Tests")

    # ✅ Hardcoded Test Elements for Debugging
    test_elements = [
        {"name": "buttons"},
        {"name": "cards"},
        {"name": "modals"},
        {"name": "forms"},
        {"name": "fetch-dashboard-data"},
        {"name": "apply-for-leave"},
        {"name": "approve-leave"},
        {"name": "login"}
    ]

    structured_input = {
        "projectName": "angular-dashboard",
        "test_elements": test_elements  
    }

    print("🔹 Running tests with input:", structured_input)

    try:
        test_status = generate_ui_tests(structured_input)  
        state["test_status"] = test_status
    except Exception as e:
        print(f"❌ Test Generation Failed: {str(e)}")
        state["test_status"] = {"error": str(e)}
        return state

    print("🚀 Running Cypress tests...")
    try:
        test_results = run_cypress_tests()
        state["test_results"] = test_results
    except Exception as e:
        print(f"❌ Cypress Test Execution Failed: {str(e)}")
        state["test_results"] = {"error": str(e)}

    return state

graph.add_node("testing_debugging_node", testing_debugging_node)

def dockerfile_generate_node(state: AgentState) -> AgentState:
    project_name = state.get("srs_data", {}).get("projectName", "angular-dashboard")

    print("🔹 Generating Dockerfile for:", project_name)
    
    try:
        state["dockerfile_status"] = generate_dockerfile(project_name)
    except Exception as e:
        print(f"❌ Dockerfile Generation Failed: {str(e)}")
        state["dockerfile_status"] = {"error": str(e)}

    return state

graph.add_node("dockerfile_generate_node", dockerfile_generate_node)

# def documentation_node(state: AgentState) -> AgentState:
#     # ⏳ Lazy import to avoid circular dependency
#     from agents.documentation_agent import generate_readme

#     # Generate the README file
#     readme_content = generate_readme(state)
#     state["documentation"] = readme_content  # Store in state if needed
    
#     return state

# Add to workflow
graph.add_node("documentation_node", documentation_agent)

graph.set_entry_point("srs_node")
graph.add_edge("srs_node", "img_node")  
graph.add_edge("img_node", "project_setup_node")  
graph.add_edge("project_setup_node", "autonomous_code_generator_node")  
graph.add_edge("autonomous_code_generator_node", "testing_debugging_node")  
graph.add_edge("testing_debugging_node", "dockerfile_generate_node")
graph.add_edge("testing_debugging_node", "documentation_node")

# ✅ Compile workflow
workflow = graph.compile()


if __name__ == "__main__":
    sample_srs_path = "data/srs.docx"
    sample_img_path = "data/dashboard_sc.png"
    
    initial_state = AgentState({
        "srs_data": {}, 
        "img_data": {},
        "project_status": "",
        "generated_components": {},
        "generated_services": {},
        "generated_pages": {},
        "code_generation_status": "",
        "srs_path": sample_srs_path,
        "img_path": sample_img_path
    })
    
    # workflow.get_graph().draw_mermaid_png(output_file_path="output/my.png")
    
    result = workflow.invoke(initial_state)

    # print(" Final Workflow Output:", result)