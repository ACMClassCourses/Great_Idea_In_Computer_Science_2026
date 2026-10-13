"""Student task: extract normalized features from frozen official CLIP ViT-B/32."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

from utils import read_manifest


class ManifestDataset(Dataset):
    def __init__(self, rows, data_root: Path, preprocess):
        self.rows, self.data_root, self.preprocess = rows, data_root, preprocess

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        with Image.open(self.data_root / row["path"]) as image:
            tensor = self.preprocess(image.convert("RGB"))
        return tensor, 1 if row["label"] == "synthetic" else 0, index


def load_backbone(device: str):
    """Load exactly the official CLIP ViT-B/32 and its own preprocess."""
    # TODO 3: Import clip and call clip.load with "ViT-B/32", the selected
    # device, and jit=False. Return both model and preprocess.
    raise NotImplementedError("TODO 3: load official CLIP ViT-B/32")


def freeze_backbone(model) -> None:
    """Put CLIP in inference mode and make every parameter non-trainable."""
    # TODO 4: Call eval(), set every parameter.requires_grad to False, and
    # assert that no parameter still requires gradients.
    raise NotImplementedError("TODO 4: freeze the CLIP backbone")


def encode(loader: DataLoader, model, device: str):
    """Return features, labels, and row indices in loader order."""
    # TODO 5: Under torch.inference_mode(), iterate over loader, move images
    # to device, call model.encode_image(), convert features to float, and
    # collect CPU NumPy arrays for features, labels, and indices.
    raise NotImplementedError("TODO 5: batch-extract CLIP image features")


def normalize_and_save(output: Path, features, labels, indices, rows) -> None:
    """L2-normalize 512-D features and save them with manifest metadata."""
    # TODO 6: L2-normalize each feature vector, verify shape (N, 512) and row
    # order, then use np.savez_compressed to save features, labels, paths,
    # sources, and splits. Create output.parent first.
    raise NotImplementedError("TODO 6: normalize, verify, and cache features")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda"))
    args = parser.parse_args()

    device = "cuda" if args.device == "auto" and torch.cuda.is_available() else args.device
    if device == "auto":
        device = "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA requested but is not available")
    rows = read_manifest(args.manifest)
    model, preprocess = load_backbone(device)
    freeze_backbone(model)
    dataset = ManifestDataset(rows, args.data_root, preprocess)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.workers)
    features, labels, indices = encode(loader, model, device)
    normalize_and_save(args.output, features, labels, indices, rows)


if __name__ == "__main__":
    main()
