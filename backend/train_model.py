"""
EfficientNet-B0 Training Script for AI vs Real Image Classification.

Dataset structure expected:
    dataset/
    ├── train/
    │   ├── real/        ← real photographs
    │   └── ai_generated/ ← AI-generated images
    ├── val/
    │   ├── real/
    │   └── ai_generated/
    └── test/
        ├── real/
        └── ai_generated/

Split: 70% train / 15% val / 15% test (no duplicates across splits)

Usage:
    cd backend
    python train_model.py --data_dir ./dataset --epochs 20 --batch_size 32

The trained model will be saved to backend/models/image_detector.pt
"""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
)


# ── CLI arguments ─────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Train AI vs Real image detector")
    p.add_argument("--data_dir",   default="./dataset",          help="Root dataset directory")
    p.add_argument("--output",     default="./models/image_detector.pt", help="Model output path")
    p.add_argument("--epochs",     type=int, default=20)
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--lr",         type=float, default=1e-4)
    p.add_argument("--img_size",   type=int, default=224)
    p.add_argument("--workers",    type=int, default=4)
    p.add_argument("--device",     default="auto",
                   help="'auto', 'cpu', or 'cuda'")
    return p.parse_args()


# ── Transforms ────────────────────────────────────────────────────────────────

def get_transforms(img_size: int):
    mean = [0.485, 0.456, 0.406]
    std  = [0.229, 0.224, 0.225]
    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(img_size),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    val_tf = transforms.Compose([
        transforms.Resize(img_size + 32),
        transforms.CenterCrop(img_size),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    return train_tf, val_tf


# ── Model ─────────────────────────────────────────────────────────────────────

def build_model() -> nn.Module:
    """EfficientNet-B0 with a 2-class head (real / ai_generated)."""
    net = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
    # Replace classifier head
    in_features = net.classifier[1].in_features
    net.classifier[1] = nn.Linear(in_features, 2)
    return net


# ── Training loop ─────────────────────────────────────────────────────────────

def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    all_preds, all_labels = [], []

    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * imgs.size(0)
        preds = outputs.argmax(dim=1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    avg_loss = running_loss / len(loader.dataset)
    acc = accuracy_score(all_labels, all_preds)
    return avg_loss, acc


@torch.no_grad()
def eval_epoch(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_preds, all_labels, all_probs = [], [], []

    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        running_loss += loss.item() * imgs.size(0)

        probs = torch.softmax(outputs, dim=1)[:, 1]   # P(ai_generated)
        preds = outputs.argmax(dim=1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
        all_probs.extend(probs.cpu().numpy())

    avg_loss = running_loss / len(loader.dataset)
    acc  = accuracy_score(all_labels, all_preds)
    prec = precision_score(all_labels, all_preds, zero_division=0)
    rec  = recall_score(all_labels, all_preds, zero_division=0)
    f1   = f1_score(all_labels, all_preds, zero_division=0)
    try:
        auc = roc_auc_score(all_labels, all_probs)
    except Exception:
        auc = float("nan")
    cm   = confusion_matrix(all_labels, all_preds).tolist()

    return avg_loss, {"accuracy": acc, "precision": prec, "recall": rec,
                      "f1": f1, "roc_auc": auc, "confusion_matrix": cm}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    # Device
    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    print(f"Using device: {device}")

    # Dataset
    data_root = Path(args.data_dir)
    assert (data_root / "train").exists(), f"train/ folder not found in {data_root}"

    train_tf, val_tf = get_transforms(args.img_size)

    train_ds = datasets.ImageFolder(data_root / "train", transform=train_tf)
    val_ds   = datasets.ImageFolder(data_root / "val",   transform=val_tf)
    test_ds  = datasets.ImageFolder(data_root / "test",  transform=val_tf)

    print(f"Classes: {train_ds.class_to_idx}")
    print(f"Train: {len(train_ds)} | Val: {len(val_ds)} | Test: {len(test_ds)}")

    # Verify class order — index 0 should be 'ai_generated', 1 'real' OR vice versa
    # The model outputs [real_prob, ai_prob] — confirm order matches
    print("Class → index mapping:", train_ds.class_to_idx)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size,
                              shuffle=True,  num_workers=args.workers, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size,
                              shuffle=False, num_workers=args.workers, pin_memory=True)
    test_loader  = DataLoader(test_ds,  batch_size=args.batch_size,
                              shuffle=False, num_workers=args.workers, pin_memory=True)

    # Model
    model     = build_model().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=args.lr)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    best_val_acc  = 0.0
    history: list = []

    print("\n── Training ──────────────────────────────────────────────────")
    for epoch in range(1, args.epochs + 1):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_metrics = eval_epoch(model, val_loader, criterion, device)
        scheduler.step()

        row = {
            "epoch":      epoch,
            "train_loss": round(train_loss, 4),
            "train_acc":  round(train_acc, 4),
            "val_loss":   round(val_loss, 4),
            **{f"val_{k}": round(v, 4) if isinstance(v, float) else v
               for k, v in val_metrics.items()},
        }
        history.append(row)
        print(f"Epoch {epoch:03d}/{args.epochs}  "
              f"train_loss={train_loss:.4f} acc={train_acc:.4f}  "
              f"val_loss={val_loss:.4f} acc={val_metrics['accuracy']:.4f} "
              f"auc={val_metrics['roc_auc']:.4f}")

        if val_metrics["accuracy"] > best_val_acc:
            best_val_acc = val_metrics["accuracy"]
            output_path  = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), output_path)
            print(f"  → Saved best model (val_acc={best_val_acc:.4f})")

    # Final test evaluation
    print("\n── Test Evaluation ───────────────────────────────────────────")
    best_model = build_model().to(device)
    best_model.load_state_dict(torch.load(args.output, map_location=device))
    _, test_metrics = eval_epoch(best_model, test_loader, criterion, device)
    print(json.dumps(test_metrics, indent=2))

    # Save training history
    hist_path = Path(args.output).parent / "training_history.json"
    with open(hist_path, "w") as f:
        json.dump({"args": vars(args), "history": history,
                   "test_metrics": test_metrics}, f, indent=2)
    print(f"\nTraining history saved to {hist_path}")
    print(f"Model saved to {args.output}")


if __name__ == "__main__":
    main()
