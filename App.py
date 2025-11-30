import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import gradio as gr

# 1. Config
# We assume the model file is in the same folder as this script for the web deployment
MODEL_PATH = "efficientnet_b0_best.pth" 
CLASSES = ['REAL', 'FAKE']

# 2. Load Model
def load_model():
    # Define the Architecture (must match your training exactly)
    model = models.efficientnet_b0(weights=None)
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, 2)
    
    # Load Weights (map_location=cpu is important for free web tiers)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()
    return model

model = load_model()

# 3. Preprocessing (Must match training transforms)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# 4. Prediction Function
def predict(image):
    if image is None:
        return None
    try:
        image_tensor = transform(image).unsqueeze(0)
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        return {CLASSES[0]: float(probabilities[0]), CLASSES[1]: float(probabilities[1])}
    except Exception as e:
        return f"Error: {e}"

# 5. The Web Interface
interface = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil", label="Upload Image"),
    outputs=gr.Label(num_top_classes=2, label="Result"),
    title="Real vs AI Image Detector",
    description="Is this image Real or AI-Generated? Upload it to find out."
)

if __name__ == "__main__":
    interface.launch()