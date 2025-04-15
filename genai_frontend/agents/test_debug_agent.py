import os
import json
import subprocess
from langchain.tools import tool
from groq import Groq
from agents.component_generate_agent import generate_ui_components
from agents.service_generate_agent import generate_services
from agents.page_generate_agent import generate_pages

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-key")
ai_client = Groq(api_key=GROQ_API_KEY)

def generate_ui_tests(input: dict) -> dict:
    """Generates Cypress tests for Angular UI elements."""
    
    project_name = input.get("projectName", "angular-dashboard")
    test_elements = input.get("test_elements", [])  

    generated_tests = {}

    for element in test_elements:
        for i in element.values():
            element_name=i

        prompt = f"""
        Generate a Cypress end-to-end test for '{element_name}'.
        Ensure it tests:
        1. Rendering the component/service/page.
        2. UI interactions (clicks, inputs, API calls).
        3. Error handling (failed requests, missing elements).
        4. Accessibility (ARIA roles, keyboard navigation).

        Return **only** the full Cypress test file (no explanations).
        """

        response = ai_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            test_code = response.choices[0].message.content
            generated_tests[element_name] = test_code


            test_dir = f"{project_name}/cypress/e2e/tests/"
            os.makedirs(test_dir, exist_ok=True)
            test_file_path = os.path.join(test_dir, f"{element_name}.cy.ts")

            with open(test_file_path, "w", encoding="utf-8") as test_file:
                test_file.write(test_code)

            print(f"✅ Generated test: {test_file_path}")

        except Exception as e:
            print(f"❌ Failed to generate test for {element_name}: {str(e)}")

    return {"status": "success", "generated_tests": list(generated_tests.keys())}


def run_cypress_tests():
    """Runs Cypress tests and captures results."""
    
    project_dir = os.path.abspath("angular-dashboard") 
    cypress_cmd = ["npx", "cypress", "run", "--spec", "cypress/e2e/tests/*"]  

    try:
        process = subprocess.Popen(
            cypress_cmd,
            cwd=project_dir,  
            stdout=subprocess.PIPE,  
            stderr=subprocess.PIPE,  
            text=True,
            shell=True  
        )

        
        for line in iter(process.stdout.readline, ''):
            print(line, end='')  

        process.stdout.close()
        process.wait()

        if process.returncode == 0:
            print("✅ Cypress tests passed successfully.")
            return {"status": "success", "output": "All tests passed!"}
        else:
            print("❌ Cypress tests failed.")
            return {"status": "failed", "output": "Some tests failed. Check logs."}
    
    except FileNotFoundError:
        print("❌ Cypress executable not found. Run 'npx cypress install'.")
        return {"status": "failed", "error": "Cypress not installed."}
    

def extract_failed_tests(log_output):
    """Parses Cypress logs to find failing test cases."""
    failed_tests = []
    lines = log_output.split("\n")

    for line in lines:
        if "FAIL" in line or "Error" in line:
            failed_tests.append(line.strip())

    return failed_tests


def debug_failing_components(state, failed_tests):
    """Re-generates failed components/services/pages up to 5 times."""
    
    retry_count = 0
    max_retries = 5

    while failed_tests and retry_count < max_retries:
        print(f"🔄 Debugging iteration {retry_count + 1}...")

        new_failed_tests = []
        for failed_test in failed_tests:
            failed_name = failed_test.split(" ")[-1].lower().replace(" ", "-")
            print(f"🚨 Re-generating {failed_name}...")

            
            if failed_name in state.get("generated_components", {}):
                structured_input = {"projectName": "angular-dashboard", "components": [{"name": failed_name}]}
                state["generated_components"][failed_name] = generate_ui_components(structured_input)
            elif failed_name in state.get("generated_services", {}):
                structured_input = {"projectName": "angular-dashboard", "services": [{"name": failed_name}]}
                state["generated_services"][failed_name] = generate_services(structured_input)
            elif failed_name in state.get("generated_pages", {}):
                structured_input = {"img_data": {"pages": [{"name": failed_name}]}}
                state["generated_pages"][failed_name] = generate_pages(structured_input)
            else:
                print(f"⚠️ Unrecognized test failure: {failed_name}")
                new_failed_tests.append(failed_name)

        retry_count += 1

        test_results = run_cypress_tests()
        failed_tests = extract_failed_tests(test_results.get("output", ""))

    if failed_tests:
        print("❌ Tests still failing after 5 attempts. Manual debugging required.")

    return state