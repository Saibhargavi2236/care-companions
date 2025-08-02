# chatbot_module.py

from transformers import pipeline

# Load generator
generator = pipeline("text-generation", model="distilgpt2")

# Simple disease-drug map for fallback recommendations
DISEASE_DRUG_MAP = {
    "type 2 diabetes mellitus": ["metformin", "glimepiride", "insulin"],
    "hypertension": ["amlodipine", "telmisartan", "lisinopril"],
    "fever": ["paracetamol", "ibuprofen"],
    "high cholesterol": ["atorvastatin"],
    "vitamin deficiency": ["vitamin b12", "vitamin d3", "calcium"]
}

def is_recommended(disease, drug):
    disease = disease.lower()
    drug = drug.lower()
    for key in DISEASE_DRUG_MAP:
        if disease in key or key in disease:
            return drug in DISEASE_DRUG_MAP[key]
    return False

def rule_based_explanation(disease, drugs):
    base = f"The patient is diagnosed with {disease}. "
    drug_effects = []

    for drug in drugs:
        if is_recommended(disease, drug):
            drug_effects.append(f"{drug.capitalize()} is commonly prescribed to manage {disease}.")
        else:
            drug_effects.append(f"{drug.capitalize()} is not typically recommended for {disease} and may not provide therapeutic benefit.")

    return base + " ".join(drug_effects)

def explain(disease, drugs):
    if not disease or not drugs:
        return "Not enough data to generate explanation."

    # Clean tokens from NER artifacts
    disease = disease.strip("#").replace("##", "").strip()
    drug_list = [d.replace("##", "").strip() for d in drugs]

    prompt = f"Patient has {disease}. Prescribed drugs: {', '.join(drug_list)}. Explain this in simple terms."

    try:
        result = generator(prompt, max_length=100, num_return_sequences=1)
        explanation = result[0]['generated_text']

        # Optionally fallback if the generation is poor or incomplete
        if len(explanation.split()) < 10 or "something" in explanation.lower():
            return rule_based_explanation(disease, drug_list)

        return explanation

    except Exception as e:
        return rule_based_explanation(disease, drug_list)
