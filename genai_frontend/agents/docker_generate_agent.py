import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-key")
ai_client = Groq(api_key=GROQ_API_KEY)

def generate_dockerfile(project_name="angular-dashboard"):
    """Generates a Dockerfile for deploying the Angular project."""


    prompt = f"""
    Generate a Dockerfile to containerize an Angular project named '{project_name}'.
    Requirements:
    - Use Node.js as the base image (latest LTS version).
    - Install dependencies and build the Angular project.
    - Serve the Angular app using **nginx**.
    - Optimize caching and minimize image size.
    - Expose port **80** for deployment.
    - Provide a **multi-stage build** for efficiency.
    """

    response = ai_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        dockerfile_content = response.choices[0].message.content
        
    
        dockerfile_path = os.path.join("angular-dashboard", "Dockerfile")
        with open(dockerfile_path, "w", encoding="utf-8") as dockerfile:
            dockerfile.write(dockerfile_content)

        print(f"✅ Dockerfile generated at: {dockerfile_path}")
        return {"status": "success", "dockerfile": dockerfile_content}

    except Exception as e:
        print(f"❌ Failed to generate Dockerfile: {str(e)}")
        return {"status": "failed", "error": str(e)}