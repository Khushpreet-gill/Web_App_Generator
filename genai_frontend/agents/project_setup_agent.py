import os
import json
import re
import sys
import subprocess
from state import AgentState  

PROJECT_NAME = "angular-dashboard"
OUTPUT_DIR = "output"
SRS_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "extracted_srs.json")

class GenerateProjectSetupAgent:
    def run(self, state: AgentState):
        """
        Executes the full Angular project setup.
        """
        extracted_details = self.load_extracted_srs()
        
        if extracted_details is None:
            print("❌ Error: Failed to load extracted SRS details.")
            state["project_status"] = "Failed"
            return state

        self.generate_project_setup(extracted_details)
        state["project_status"] = "Project setup completed"
        return state

    def load_extracted_srs(self):
        """
        Loads and cleans extracted JSON from the SRS file.
        """
        if not os.path.exists(SRS_OUTPUT_FILE):
            print("❌ Error: Extracted SRS data not found. Run `process_srs` first.")
            return None

        with open(SRS_OUTPUT_FILE, "r", encoding="utf-8") as f:
            raw_data = f.read().strip()

        
        try:
            extracted_json = json.loads(raw_data)
            return extracted_json  
        except json.JSONDecodeError:
            print("⚠️ Warning: JSON is not directly parsable. Attempting cleanup.")

        json_match = re.search(r"```json\n(.*?)\n```", raw_data, re.DOTALL)
        if not json_match:
            print("❌ Error: JSON structure not found in SRS output.")
            return None

        try:
            cleaned_json = json.loads(json_match.group(1))
            return cleaned_json
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parsing Error: {str(e)}")
            return None

    def generate_project_setup(self, extracted_details):
        """
        Initializes the Angular project and generates components & services dynamically.
        """
        self.initialize_angular_project()
        self.setup_state_management()
        self.install_dependencies()
        self.setup_cypress()
        self.define_folder_structure()
        self.generate_components_and_services(extracted_details)

    def initialize_angular_project(self):
        if not os.path.exists(PROJECT_NAME):
            os.system(f"ng new {PROJECT_NAME} --routing --style=scss")
        else:
            print(f"⚠️ Angular project '{PROJECT_NAME}' already exists. Skipping creation.")

    def setup_state_management(self):
        os.system(f"cd {PROJECT_NAME} && ng add @ngrx/store")

    def install_dependencies(self):
        dependencies = [
            "@angular/material", "rxjs",
            "@ngrx/store", "@ngrx/effects",
            "cypress"  # 
        ]
        os.system(f"cd angular-dashboard && npm install {' '.join(dependencies)}")

    def setup_cypress(self):
        """Initializes Cypress in the Angular project."""
        os.system("cd angular-dashboard && npx cypress open --config-file false")
        print("✅ Cypress initialized with default configuration.")

    def define_folder_structure(self):
        folders = ["src/app/components", "src/app/services"]
        for folder in folders:
            os.makedirs(os.path.join(PROJECT_NAME, folder), exist_ok=True)

    def generate_components_and_services(self, extracted_details):
        """
        Dynamically generates Angular components and services based on the cleaned JSON data.
        """
        components = extracted_details.get("uiComponents", [])  
        services = extracted_details.get("apiEndPoints", [])  

        for component in components:
            component_name = component.get("name", "UnnamedComponent").lower()
            component_path = os.path.join(PROJECT_NAME, f"src/app/components/{component_name}")
            os.makedirs(component_path, exist_ok=True)

            ts_file = os.path.join(component_path, f"{component_name}.component.ts")
            with open(ts_file, "w") as ts:
                ts.write(f"export class {component_name.capitalize()}Component {{}}")
            print(f"✅ Created Component: {component_name}")

        for service in services:
            service_name = service.get("name", "UnnamedService").replace(" ", "").lower()
            service_path = os.path.join(PROJECT_NAME, f"src/app/services/{service_name}.service.ts")

            with open(service_path, "w") as service_file:
                service_file.write(f"export class {service_name.capitalize()}Service {{}}")
            print(f"✅ Created Service: {service_name}")