import os
import shutil
from fastapi import FastAPI, File, UploadFile
from agents.srs_agent import process_srs
from agents.img_agent import process_image

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure upload folder exists

@app.post("/process-srs/")
async def process_srs_endpoint(srs_file: UploadFile = File(...), img_file: UploadFile = File(...)):
    """
    Endpoint to process an SRS .docx file and UI screenshot image.
    Returns structured JSON data from both.
    """
    # Save the uploaded files
    srs_path = os.path.join(UPLOAD_DIR, srs_file.filename)
    img_path = os.path.join(UPLOAD_DIR, img_file.filename)
    
    with open(srs_path, "wb") as srs_out:
        shutil.copyfileobj(srs_file.file, srs_out)
    
    with open(img_path, "wb") as img_out:
        shutil.copyfileobj(img_file.file, img_out)

    # Process the files using existing agents
    srs_data = process_srs(srs_path)
    img_data = process_image(img_path)

    print(srs_data,img_data)

    return {
        "srs_data": srs_data,
        "img_data": img_data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)