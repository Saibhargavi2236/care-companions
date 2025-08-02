from transformers import pipeline
import re

ner = pipeline("ner", model="d4data/biomedical-ner-all", aggregation_strategy="simple")

COMMON_DISEASES = [
    "type 2 diabetes", "type 1 diabetes", "hypertension", "thyroid disorder",
    "asthma", "arthritis", "tuberculosis"
]

COMMON_DRUGS = [
    "metformin", "glimepiride", "atorvastatin", "vitamin d3", "vitamin b12",
    "levothyroxine", "amlodipine", "telmisartan", "calcium", "paracetamol", "ibuprofen"
]

def clean_tokens(tokens):
    merged = []
    i = 0
    while i < len(tokens):
        word = tokens[i]
        if word.startswith("##") and merged:
            merged[-1] += word[2:]
        else:
            merged.append(word)
        i += 1
    # Normalize
    cleaned = list(set([w.strip().lower() for w in merged if w]))
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

    # Clean up tokenization artifacts
    diseases = clean_tokens(diseases)
    drugs = clean_tokens(drugs)

    # Fallback matching if extraction fails
    if not diseases:
        for d in COMMON_DISEASES:
            if re.search(rf"\b{re.escape(d)}\b", text.lower()):
                diseases.append(d)

    if not drugs:
        for drug in COMMON_DRUGS:
            if re.search(rf"\b{re.escape(drug)}\b", text.lower()):
                drugs.append(drug)

    return list(set(diseases)), list(set(drugs))
