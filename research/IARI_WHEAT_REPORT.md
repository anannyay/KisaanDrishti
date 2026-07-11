# IARI wheat baseline training report

## Dataset

Wheat Nitrogen Deficiency and Leaf Rust Image Dataset, collected during the 2019–20 rabi season at an IARI field. DOI: `10.17632/th422bg4yd.1`. Dataset use requires attribution under CC BY 4.0.

## Preparation

The source contains two nested archives. CropPulse streams both without a full extraction, verifies every image, normalizes orientation, fits it onto a 224×224 canvas and retains the authors' train/validation/test design. SHA-256 comparison removed 70 exact duplicate files before training; no corrupt images were found.

| Split | Healthy | Leaf rust | Nitrogen deficient |
|---|---:|---:|---:|
| Train | 547 | 258 | 149 |
| Validation | 119 | 54 | 45 |
| Test | 118 | 54 | 45 |

## Model

A compact depthwise CNN was trained from scratch for 10 epochs with geometric and colour augmentation, AdamW, label smoothing and cosine learning-rate decay. Training used CPU and selected the checkpoint with the lowest validation loss.

## Held-out results

- Accuracy: 0.9032
- Macro-F1: 0.8839
- Confusion matrix, rows/columns in `healthy`, `leaf_rust`, `nitrogen_deficient` order:

```text
116   0   2
  3  51   0
 16   0  29
```

Leaf rust is strongly separated in this dataset. Nitrogen deficiency is the largest source of error, with 16 of 45 test examples predicted as healthy. This is a meaningful limitation rather than a result to hide.

## Reproduce

```bash
python research/prepare_iari_wheat.py
python research/train_wheat_cnn.py --epochs 10 --batch-size 32
python -m unittest discover -s backend -p "test_*.py" -v
```

Source archives, compact images and experimental artifacts are excluded from Git. The selected 804 KB deployment checkpoint and recorded metrics are versioned under `backend/models/`.
