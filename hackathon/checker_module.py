from transformers import pipeline
import re

ner = pipeline("ner", model="d4data/biomedical-ner-all", aggregation_strategy="simple")

COMMON_DRUGS = [
    "metformin", "glimepiride", "atorvastatin", "vitamin d3", "levothyroxine",
    "amlodipine", "telmisartan", "calcium", "paracetamol", "ibuprofen"
]

# Sample curated drug–disease mapping
DISEASE_DRUG_MAP = {
    "type 2 diabetes mellitus": ["metformin", "glimepiride", "insulin"],
    "type 2 diabetes": ["metformin", "glimepiride", "insulin"],
    "hypertension": ["amlodipine", "telmisartan", "atenolol", "losartan"],
    "hypothyroidism": ["levothyroxine"],
    "pain": ["paracetamol", "ibuprofen"]
}

def clean_tokens(tokens):
    cleaned = []
    for token in tokens:
        token = token.replace("##", "").strip().lower()
        if token and token not in cleaned:
            cleaned.append(token)
    return cleaned

def extract_entities(text):
    result = ner(text)
    diseases = []
    drugs = []

    for ent in result:
        label = ent["entity_group"].upper()
        word = ent["word"].strip().lower()
        if "DISEASE" in label:
            diseases.append(word)
        elif "DRUG" in label:
            drugs.append(word)

    # Post-process cleaning
    diseases = clean_tokens(diseases)
    drugs = clean_tokens(drugs)

    # Fallback drug extraction
    if not drugs:
        for drug in COMMON_DRUGS:
            if re.search(rf"\b{re.escape(drug)}\b", text.lower()):
                drugs.append(drug)

    return diseases, drugs

def check_match(diseases, drugs):
    matches = []
    for disease in diseases:
        for drug in drugs:
            recommended = drug in DISEASE_DRUG_MAP.get(disease, [])
            matches.append({
                "drug": drug,
                "disease": disease,
                "recommended": recommended
            })
    return matches

def generate_explanation(diseases, drugs, matches):
    if not diseases:
        return "No diseases were identified. Cannot generate explanation."
    if not drugs:
        return "No drugs were identified. Cannot generate explanation."

    valid = [m for m in matches if m["recommended"]]
    if not valid:
        return (
            "The prescribed drugs do not appear to match the diagnosed diseases based on common clinical guidelines. "
            "Please consult a healthcare professional to verify the prescription."
        )

    # Template-based explanations
    explanation_parts = []
    for match in valid:
        disease = match["disease"]
        drug = match["drug"]

        if drug == "telmisartan" and disease == "hypertension":
            explanation_parts.append("Telmisartan is used to treat hypertension by relaxing blood vessels, making it easier for the heart to pump blood.")
        elif drug == "vitamin d3":
            explanation_parts.append("Vitamin D3 helps in overall health and may support cardiovascular function in hypertensive patients.")
        elif drug == "metformin" and disease in ["type 2 diabetes", "type 2 diabetes mellitus"]:
            explanation_parts.append("Metformin helps control blood sugar levels in patients with type 2 diabetes.")
        elif drug == "glimepiride" and disease in ["type 2 diabetes", "type 2 diabetes mellitus"]:
            explanation_parts.append("Glimepiride stimulates insulin release from the pancreas to lower blood sugar.")
        elif drug == "levothyroxine" and disease == "hypothyroidism":
            explanation_parts.append("Levothyroxine replaces or provides more thyroid hormone, which is normally produced by the thyroid gland.")
        elif drug == "paracetamol" and disease == "pain":
            explanation_parts.append("Paracetamol is commonly used to relieve mild to moderate pain.")
        elif drug == "ibuprofen" and disease == "pain":
            explanation_parts.append("Ibuprofen reduces pain, inflammation, and fever.")

    return " ".join(explanation_parts)

# Export for API use
is_drug_relevant = check_match
