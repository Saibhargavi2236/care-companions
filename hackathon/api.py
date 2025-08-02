from fastapi import FastAPI, UploadFile, File, HTTPException, Form
import traceback
from ocr_module import extract_text
from nlp_module import extract_entities
from checker_module import is_drug_relevant
from chatbot_module import explain

app = FastAPI()

@app.post("/analyze/")
async def analyze(file: UploadFile = File(None), text: str = Form(None)):
    try:
        if file:
            with open("temp.jpg", "wb") as f:
                f.write(await file.read())
            text = extract_text("temp.jpg")

        if not text:
            raise HTTPException(status_code=400, detail="Either text or image must be provided.")

        diseases, drugs = extract_entities(text)
        matches = [(disease, drug, is_drug_relevant(disease, drug)) for disease in diseases for drug in drugs]
        explanation = explain(diseases[0], drugs) if diseases and drugs else "Could not generate."

        return {
            "text": text,
            "diseases": diseases,
            "drugs": drugs,
            "matches": matches,
            "explanation": explanation
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
