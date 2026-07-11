"""Train a compact three-class RGB baseline for CropPulse."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import classification_report, confusion_matrix
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


class WheatHealthNet(nn.Module):
    def __init__(self, classes: int = 3):
        super().__init__()
        channels = [3, 24, 48, 96, 160]
        blocks = []
        for left, right in zip(channels, channels[1:]):
            blocks += [nn.Conv2d(left, right, 3, stride=2, padding=1, bias=False), nn.BatchNorm2d(right), nn.SiLU(),
                       nn.Conv2d(right, right, 3, padding=1, groups=right, bias=False), nn.BatchNorm2d(right), nn.SiLU()]
        self.features = nn.Sequential(*blocks)
        self.head = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Dropout(.25), nn.Linear(channels[-1], classes))

    def forward(self, image: torch.Tensor) -> torch.Tensor:
        return self.head(self.features(image))


def seed_all(seed: int = 42) -> None:
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def evaluate(model, loader, device):
    model.eval(); truth=[]; prediction=[]; loss_total=0.; criterion=nn.CrossEntropyLoss()
    with torch.no_grad():
        for images, labels in loader:
            images, labels=images.to(device), labels.to(device); logits=model(images)
            loss_total += criterion(logits, labels).item()*len(labels)
            truth.extend(labels.cpu().tolist()); prediction.extend(logits.argmax(1).cpu().tolist())
    return loss_total/len(loader.dataset), truth, prediction


def train(data: Path, output: Path, epochs: int = 12, batch_size: int = 32) -> dict:
    seed_all(); device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_tf=transforms.Compose([transforms.RandomResizedCrop(192, scale=(.72,1.0)), transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(12), transforms.ColorJitter(.15,.15,.12,.04), transforms.ToTensor(),
        transforms.Normalize([.485,.456,.406],[.229,.224,.225])])
    eval_tf=transforms.Compose([transforms.Resize((192,192)),transforms.ToTensor(),transforms.Normalize([.485,.456,.406],[.229,.224,.225])])
    sets={"train":datasets.ImageFolder(data/"train",train_tf),"val":datasets.ImageFolder(data/"val",eval_tf),"test":datasets.ImageFolder(data/"test",eval_tf)}
    if sets["train"].classes != sets["val"].classes or sets["train"].classes != sets["test"].classes:
        raise ValueError("Class folders differ between splits")
    loaders={name:DataLoader(ds,batch_size=batch_size,shuffle=name=="train",num_workers=0) for name,ds in sets.items()}
    model=WheatHealthNet(len(sets["train"].classes)).to(device); optimizer=torch.optim.AdamW(model.parameters(),lr=8e-4,weight_decay=1e-3)
    scheduler=torch.optim.lr_scheduler.CosineAnnealingLR(optimizer,epochs); criterion=nn.CrossEntropyLoss(label_smoothing=.05)
    output.mkdir(parents=True,exist_ok=True); best=float("inf"); history=[]
    for epoch in range(1,epochs+1):
        model.train(); total=0.
        for images,labels in loaders["train"]:
            images,labels=images.to(device),labels.to(device);optimizer.zero_grad();loss=criterion(model(images),labels);loss.backward();optimizer.step();total+=loss.item()*len(labels)
        val_loss,truth,pred=evaluate(model,loaders["val"],device); scheduler.step()
        row={"epoch":epoch,"train_loss":round(total/len(sets["train"]),5),"val_loss":round(val_loss,5),"val_accuracy":round(float(np.mean(np.array(truth)==pred)),5)};history.append(row);print(row)
        if val_loss<best:
            best=val_loss;torch.save({"state_dict":model.state_dict(),"classes":sets["train"].classes,"input_size":192},output/"wheat_health_best.pt")
    checkpoint=torch.load(output/"wheat_health_best.pt",map_location=device,weights_only=True);model.load_state_dict(checkpoint["state_dict"])
    test_loss,truth,pred=evaluate(model,loaders["test"],device)
    report=classification_report(truth,pred,target_names=checkpoint["classes"],output_dict=True,zero_division=0)
    metrics={"device":str(device),"classes":checkpoint["classes"],"test_loss":test_loss,"test_accuracy":float(np.mean(np.array(truth)==pred)),
             "macro_f1":report["macro avg"]["f1-score"],"confusion_matrix":confusion_matrix(truth,pred).tolist(),"classification_report":report,"history":history}
    (output/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8");return metrics


def main():
    p=argparse.ArgumentParser();p.add_argument("--data",type=Path,default=Path("data/processed/iari_wheat_224"));p.add_argument("--output",type=Path,default=Path("artifacts/wheat_cnn"));p.add_argument("--epochs",type=int,default=12);p.add_argument("--batch-size",type=int,default=32);a=p.parse_args();m=train(a.data,a.output,a.epochs,a.batch_size);print(json.dumps({k:m[k] for k in ['device','test_accuracy','macro_f1','confusion_matrix']},indent=2))


if __name__=="__main__":main()
