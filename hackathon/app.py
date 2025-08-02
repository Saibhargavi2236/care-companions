# Updated app.py with improved formatting and output clarity
import streamlit as st
import requests

st.set_page_config(page_title="Prescription Verifier", page_icon="🩺", layout="centered")
st.title("🩺 AI Medical Prescription Verifier")
st.markdown("""
This tool analyzes a prescription image or text input to:
- Extract diseases and drugs
- Check if prescribed drugs are appropriate for the condition
- Explain the drug–disease relationship in simple terms
""")

option = st.radio("Choose Input Type:", ("Upload Image", "Enter Text"))

if option == "Upload Image":
    uploaded_file = st.file_uploader("Upload Prescription Image", type=['jpg', 'jpeg', 'png'])

    if uploaded_file and st.button("Analyze Prescription"):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post("http://127.0.0.1:8000/analyze/", files=files)

        if response.ok:
            data = response.json()
            st.subheader("🔍 Extracted Information")

            st.markdown("**🦠 Identified Diseases:**")
            st.write(", ".join(data.get('diseases', [])) or "None")

            st.markdown("**💊 Identified Drugs:**")
            st.write(", ".join(data.get('drugs', [])) or "None")

            st.markdown("**⚖️ Disease–Drug Matching:**")
            for disease, drug, is_match in data.get('matches', []):
                st.write(f"💊 {drug} for 🦠 {disease} — {'✅ Match' if is_match else '❌ Not Recommended'}")

            st.markdown("**🧠 Explanation:**")
            st.write(data.get('explanation', 'No explanation available.'))

        else:
            st.error("Something went wrong while analyzing the image.")
            st.text(f"Status Code: {response.status_code}")
            st.text(response.text)

elif option == "Enter Text":
    input_text = st.text_area("Paste the Prescription Text")

    if input_text and st.button("Analyze Prescription"):
        response = requests.post("http://127.0.0.1:8000/analyze/", data={"text": input_text})

        if response.ok:
            data = response.json()
            st.subheader("🔍 Extracted Information")

            st.markdown("**🦠 Identified Diseases:**")
            st.write(", ".join(data.get('diseases', [])) or "None")

            st.markdown("**💊 Identified Drugs:**")
            st.write(", ".join(data.get('drugs', [])) or "None")

            st.markdown("**⚖️ Disease–Drug Matching:**")
            for disease, drug, is_match in data.get('matches', []):
                st.write(f"💊 {drug} for 🦠 {disease} — {'✅ Match' if is_match else '❌ Not Recommended'}")

            st.markdown("**🧠 Explanation:**")
            st.write(data.get('explanation', 'No explanation available.'))

        else:
            st.error("Something went wrong while analyzing the text.")
            st.text(f"Status Code: {response.status_code}")
            st.text(response.text)
