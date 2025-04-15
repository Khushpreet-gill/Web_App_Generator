import json
from PIL import Image
import requests
import base64
import os
from groq import Groq
import re

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
client = Groq(api_key=GROQ_API_KEY)

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def process_image(image_path: str) -> dict:
    def encode_image(image_path):
        """Encodes a local image file to a base64 string."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError:
            return None

    """
    Uses Llama 3 Vision (Groq Preview) to extract UI design details from a screenshot.
    """
    prompt = """Analyze this UI screenshot and extract structured details:
    - UI Components (buttons, forms, tables, modals, navigation)
    - Layout structure
    - Styling & theme (colors, fonts, spacing)
    - Accessibility features
    
    Return structured JSON output."""

    image_base64 = encode_image(image_path)
    if not image_base64:
        return {"error": "Image file not found"}

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze the screenshot and extract UI details"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }
        ],
        max_tokens=1000
    )

    try:
        response_json = response.choices[0].message.content
        print("🔹 Raw API Response:", json.dumps(response_json, indent=2))  # Debugging Step
        structured = parse_response_to_json(response_json)
        # Save the extracted data to a JSON file
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, "extracted_img.json")

        with open(output_file_path, "w") as output_file:
                json.dump(structured, output_file, indent=2)

        # print(structured)
        return structured
    except Exception as e:
        return {"error": f"Failed to process API response: {str(e)}"}
    
def parse_response_to_json(response_text: str) -> dict:
    """Parses the raw response text into a structured JSON format."""

    def extract_sections(text):
        sections = {}
        current_section = None
        current_content = []

        for line in text.splitlines():
            section_match = re.match(r"\*\*(.*?)\*\*", line)
            if section_match:
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = section_match.group(1)
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def parse_list_items(text):
        items = []
        for item in text.split("\n* "):
            if item.strip():
                items.append(item.strip())
        return items

    sections = extract_sections(response_text)
    structured_data = {section: parse_list_items(content) for section, content in sections.items()}

    return structured_data

# Example usage
# if __name__ == "__main__":
#     image_path = "data/dashboard_sc.png"
#     result = process_image(image_path)
#     print("Processed Image Data:", result)
