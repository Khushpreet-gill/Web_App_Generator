import json
import docx
import requests
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def extract_text_from_docx(docx_path):
    """
    Extracts readable text from a .docx file.
    """
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def process_srs(srs_path: str) -> dict:
    """
    Uses Llama 3 Vision (Groq Preview) to analyze the SRS document and extract structured data.
    """
    prompt = """Extract the relevant frontend development details from this SRS document.
    Ensure the response is a **valid JSON object only** with the following structure:

    {
    "projectName": "<string>",
    "dependencies": ["<list_of_dependencies>"],
    "uiComponents": [
        {
        "name": "<component_name>",
        "description": "<brief_description>"
        }
    ],
    "stateManagement": {
        "globalState": "<description>",
        "apiHandling": "<description>",
        "interactions": "<description>"
    },
    "apiEndPoints": [
        {
        "name": "<API name>",
        "method": "<HTTP method>",
        "endpoint": "<API URL>",
        "headers": ["<list_of_headers>"],
        "body": { "<example_request_body>" },
        "response": { "<example_response>" }
        }
    ],
    "stylingAndBranding": {
        "colorScheme": {
        "primaryColor": "<hex_code>",
        "secondaryColor": "<hex_code>"
        },
        "typography": {
        "fontFamily": "<font>",
        "headingFontSize": <number>,
        "bodyFontSize": <number>
        }
    }
    }

    Strictly **return only JSON** without any additional text or markdown.
    """

    
    srs_text = extract_text_from_docx(srs_path)

    response = requests.post(
        GROQ_ENDPOINT,
        headers=HEADERS,
        json={
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": srs_text}
            ],
            "max_tokens": 2000
        }
    )

    try:
        response_json = response.json()
        print("🔹 Raw API Response:", json.dumps(response_json, indent=2))  

        if "choices" in response_json and response_json["choices"]:
            data = response_json["choices"][0]["message"]["content"]

            
            data_dict = json.loads(data)

            
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            output_file_path = os.path.join(output_dir, "extracted_srs.json")

            with open(output_file_path, "w") as output_file:
                json.dump(data_dict, output_file, indent=2)

            print(data_dict)
            return data_dict
        else:
            return {"error": "No choices returned from Llama 3 Vision"}

    except Exception as e:
        return {"error": f"Failed to process API response: {str(e)}"}