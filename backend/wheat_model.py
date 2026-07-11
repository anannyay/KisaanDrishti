"""Inference adapter for the IARI wheat crop-health baseline."""
from io import BytesIO
from pathlib import Path
import torch
from PIL import Image, ImageOps
from torch import nn
from torchvision import transforms

class WheatHealthNet(nn.Module):
    def __init__(self, classes=3):
        super().__init__(); channels=[3,24,48,96,160]; blocks=[]
        for left,right in zip(channels,channels[1:]):
            blocks += [nn.Conv2d(left,right,3,stride=2,padding=1,bias=False),nn.BatchNorm2d(right),nn.SiLU(),nn.Conv2d(right,right,3,padding=1,groups=right,bias=False),nn.BatchNorm2d(right),nn.SiLU()]
        self.features=nn.Sequential(*blocks); self.head=nn.Sequential(nn.AdaptiveAvgPool2d(1),nn.Flatten(),nn.Dropout(.25),nn.Linear(channels[-1],classes))
    def forward(self,image): return self.head(self.features(image))

MODEL_PATH=Path(__file__).parent/"models"/"wheat_health_best.pt"
_checkpoint=torch.load(MODEL_PATH,map_location="cpu",weights_only=True)
_model=WheatHealthNet(len(_checkpoint["classes"]));_model.load_state_dict(_checkpoint["state_dict"]);_model.eval()
_transform=transforms.Compose([transforms.Resize((_checkpoint["input_size"],_checkpoint["input_size"])),transforms.ToTensor(),transforms.Normalize([.485,.456,.406],[.229,.224,.225])])

def predict_wheat(payload: bytes) -> dict:
    image=ImageOps.exif_transpose(Image.open(BytesIO(payload))).convert("RGB")
    with torch.inference_mode(): probabilities=torch.softmax(_model(_transform(image).unsqueeze(0)),1)[0]
    scores={label:round(float(probabilities[i]),4) for i,label in enumerate(_checkpoint["classes"])}
    label=max(scores,key=scores.get);confidence=scores[label]
    return {"label":label,"confidence":confidence,"probabilities":scores,"model":"iari-wheat-cnn-v1","reliable":confidence>=.65,"scope":"Indian wheat leaves at booting stage: healthy, nitrogen deficient, or leaf rust.","disclaimer":"Research prediction only; confirm with an agronomist before taking action."}
