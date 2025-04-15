import os
import json
import base64
from langchain.tools import tool
from groq import Groq


PROJECT_NAME = "angular-dashboard"
PAGES_DIR = os.path.join(PROJECT_NAME, "src/app/pages")
OUTPUT_DIR = "output"


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-key")
ai_client = Groq(api_key=GROQ_API_KEY)

def encode_image(image_path):
    """Encodes a local image file to base64 for Llama 3 Vision."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return None

def process_image_with_llm(image_path):
    """Uses Llama 3 Vision to extract UI details from a page screenshot."""
    image_base64 = encode_image(image_path)
    if not image_base64:
        return {"error": "Image file not found"}

    prompt = "Analyze this UI screenshot and extract all visible UI elements in JSON format."

    response = ai_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                ],
            },
        ],
    )

    try:
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": f"Failed to process image with LLM: {str(e)}"}

def generate_pages(input: dict) -> dict:
    """
    Reads extracted UI details from img_data and predefined logic, then generates Angular page components.
    """

    pages = ["dashboard", "login", "pods"]
    generated_pages = {}

    for page in pages:
        if page in ["login", "pods"]:
            image_path = os.path.join(OUTPUT_DIR, f"{page}.png")
            if os.path.exists(image_path):
                print(f"📸 Processing {page}.png through Llama 3 Vision...")
                ui_details = process_image_with_llm(image_path)
            else:
                ui_details = {"error": f"Image {page}.png not found"}
        else:
            ui_details = {"message": f"Using predefined layout for {page} page"}

        prompt = f"""
        Generate an Angular page component for '{page}' with:
        - TypeScript (`{page}.component.ts`): Implements Angular logic.
        - HTML (`{page}.component.html`): UI structure based on extracted data.
        - SCSS (`{page}.component.scss`): Styling consistent with branding.

        Page details:
        {json.dumps(ui_details, indent=2)}

        Return only the full TypeScript file with embedded HTML & SCSS.
        """

        response = ai_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            ts_code = response.choices[0].message.content
            generated_pages[page] = ts_code

            # Step 3: Save the `.ts` file
            page_dir = os.path.join(PAGES_DIR, page)
            os.makedirs(page_dir, exist_ok=True)
            ts_file_path = os.path.join(page_dir, f"{page}.component.ts")

            with open(ts_file_path, "w", encoding="utf-8") as ts_file:
                ts_file.write(ts_code)

            print(f"✅ Generated page: {ts_file_path}")

        except Exception as e:
            print(f"❌ Failed to generate page {page}: {str(e)}")

    return {
        "status": "success",
        "generated_pages": list(generated_pages.keys())
                                                        }