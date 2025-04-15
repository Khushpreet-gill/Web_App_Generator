import os
import json
from langchain.tools import tool
from groq import Groq


PROJECT_NAME = "angular-dashboard"
OUTPUT_DIR = "output"
SERVICES_DIR = os.path.join(PROJECT_NAME, "src/app/services")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-key")
ai_client = Groq(api_key=GROQ_API_KEY)

def clear_services_folder():
    """Deletes all existing service files in `src/app/services/` before generating new ones."""
    if os.path.exists(SERVICES_DIR):
        for file in os.listdir(SERVICES_DIR):
            file_path = os.path.join(SERVICES_DIR, file)
            if file.endswith(".service.ts"):
                os.remove(file_path)
                # print(f"🗑 Deleted old service file: {file_path}")
    else:
        os.makedirs(SERVICES_DIR, exist_ok=True)
        print(f"📂 Created empty services directory: {SERVICES_DIR}")

def generate_services(input: dict) -> dict:
    """
    Reads predefined service details from SRS JSON and generates Angular service files.
    """

    services = input.get("services", [])

    if not services:
        print("⚠️ No services found in extracted SRS.")
        return {"status": "no_services", "message": "No services to generate."}
    
    clear_services_folder()

    generated_services = {}

    
    for service in services:
        service_name = service["name"].lower().replace(" ", "-")

        prompt = f"""
        Generate an Angular service for '{service_name}' with:
        - Proper dependency injection using `HttpClient`.
        - API methods based on extracted SRS endpoints.
        - Error handling with RxJS `catchError`.
        - Follow Angular best practices.

        **Return only the full TypeScript code for `{service_name}.service.ts`**
        """

        response = ai_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            ts_code = response.choices[0].message.content
            generated_services[service_name] = ts_code

            
            service_dir = os.path.join(PROJECT_NAME, "src/app/services")
            os.makedirs(service_dir, exist_ok=True)
            ts_file_path = os.path.join(service_dir, f"{service_name}.service.ts")

            with open(ts_file_path, "w", encoding="utf-8") as ts_file:
                ts_file.write(ts_code)

            print(f"✅ Generated service: {ts_file_path}")

        except Exception as e:
            print(f"❌ Failed to generate service {service_name}: {str(e)}")

    return {
        "status": "success",
        "generated_services": list(generated_services.keys())
    }