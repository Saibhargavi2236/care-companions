from transformers import VisionEncoderDecoderModel, TrOCRProcessor
from PIL import Image
import torch

# Load processor and model once globally
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-small-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-small-handwritten")

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def extract_text(image_path):
    try:
        image = Image.open(image_path).convert("RGB")

        # Preprocess image and move to appropriate device
        pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)

        # Generate text
        generated_ids = model.generate(pixel_values)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return generated_text

    except Exception as e:
        return f"Error processing image: {str(e)}"
