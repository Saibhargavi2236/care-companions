from ocr_module import extract_text

# Use the full path to any image you want to test
text = extract_text("C:/Users/saibh/hackathon/temp.jpg")  # update this path to your actual file
print(f"\n📝 Extracted Text:\n{text}\n")
