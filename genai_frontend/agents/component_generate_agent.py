import os
import json
from langchain.tools import tool
from groq import Groq

# Project and output directories
PROJECT_NAME = "angular-dashboard"
OUTPUT_DIR = "output"
SRS_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "extracted_srs.json")

# Initialize Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-key")
ai_client = Groq(api_key=GROQ_API_KEY)

def generate_ui_components(input: dict) -> dict:
    """
    Reads extracted UI details from SRS JSON and generates Angular component files 
    with TypeScript, HTML, and SCSS in a single `.ts` file.
    """

    # Step 1: Load extracted SRS details
    # if not os.path.exists(SRS_OUTPUT_FILE):
    #     print("❌ Error: Extracted SRS details not found. Run `process_srs` first.")
    #     return {"status": "failed", "reason": "SRS data missing"}

    # with open(SRS_OUTPUT_FILE, "r", encoding="utf-8") as f:
    #     srs_details = json.load(f)

    components = input.get("components", [])

    if not components:
        print("⚠️ No components found in extracted SRS.")
        return {"status": "no_components", "message": "No components to generate."}

    generated_components = {}

    # Step 2: Generate Angular component files
    for component in components:
        component_name = component["name"].lower().replace(" ", "-")

        prompt = f"""
        Generate an Angular component for '{component_name}' with:
        1. TypeScript (`{component_name}.component.ts`): Implements Angular logic.
        2. HTML (`{component_name}.component.html`): Basic UI structure.
        3. SCSS (`{component_name}.component.scss`): Styling.

        **Ensure the entire code (TS, HTML, and SCSS) is inside one TypeScript file as a string template.**

        Component details:
        {json.dumps(component, indent=2)}

        Return only the full TypeScript file with embedded HTML & SCSS.
        """

        response = ai_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            ts_code = response.choices[0].message.content
            generated_components[component_name] = ts_code

            # Step 3: Save the `.ts` file with embedded HTML & SCSS
            component_dir = os.path.join(PROJECT_NAME, f"src/app/components/{component_name}")
            os.makedirs(component_dir, exist_ok=True)
            ts_file_path = os.path.join(component_dir, f"{component_name}.component.ts")

            with open(ts_file_path, "w", encoding="utf-8") as ts_file:
                ts_file.write(ts_code)

            print(f"✅ Generated component: {ts_file_path}")

        except Exception as e:
            print(f"❌ Failed to generate component {component_name}: {str(e)}")

    return {
        "status": "success",
        "generated_components": list(generated_components.keys())
              }