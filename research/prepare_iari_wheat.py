"""Stream and compact the nested IARI wheat archive without full extraction."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
from collections import Counter
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from PIL import Image, ImageOps

CLASS_MAP = {"control": "healthy", "deficiency": "nitrogen_deficient", "diseased": "leaf_rust"}
SPLIT_ORDER = {"train": 0, "val": 1, "test": 2}


def prepare(archive: Path, output: Path, size: int = 224) -> dict[str, int]:
    seen: set[str] = set(); manifest_rows = []; counts: Counter[str] = Counter()
    corrupt = 0; duplicates = 0; index = 0
    with ZipFile(archive) as outer:
        # Iterating by split ensures any duplicate is retained in train before
        # validation/test, without holding decoded images in memory.
        for requested_split in ("train", "val", "test"):
            for nested_info in outer.infolist():
                if not nested_info.filename.lower().endswith(".zip"):
                    continue
                source = PurePosixPath(nested_info.filename).stem
                with ZipFile(io.BytesIO(outer.read(nested_info))) as nested:
                    for info in nested.infolist():
                        if not info.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                            continue
                        parts = PurePosixPath(info.filename).parts
                        if len(parts) < 4 or parts[-3] != requested_split or parts[-2] not in CLASS_MAP:
                            continue
                        raw = nested.read(info); digest = hashlib.sha256(raw).hexdigest()
                        if digest in seen:
                            duplicates += 1
                            continue
                        try:
                            image = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
                            image.load()
                        except Exception:
                            corrupt += 1
                            continue
                        seen.add(digest); label = CLASS_MAP[parts[-2]]
                        target_dir = output / requested_split / label
                        target_dir.mkdir(parents=True, exist_ok=True)
                        target = target_dir / f"{source.lower()}_{index:05d}.jpg"
                        compact = ImageOps.contain(image, (size, size), Image.Resampling.LANCZOS)
                        canvas = Image.new("RGB", (size, size), (245, 245, 245))
                        canvas.paste(compact, ((size - compact.width) // 2, (size - compact.height) // 2))
                        canvas.save(target, "JPEG", quality=86, optimize=True)
                        counts[f"{requested_split}/{label}"] += 1; index += 1
                        manifest_rows.append({"source":source,"original":info.filename,"split":requested_split,
                                              "class":label,"sha256":digest,"processed_path":target.relative_to(output).as_posix()})
    output.mkdir(parents=True, exist_ok=True)
    with (output / "manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest_rows[0].keys())
        writer.writeheader(); writer.writerows(manifest_rows)
    summary = dict(sorted(counts.items())) | {"total": len(manifest_rows), "exact_duplicates_removed": duplicates, "corrupt_removed": corrupt}
    (output / "summary.txt").write_text("\n".join(f"{k}: {v}" for k, v in summary.items()), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, default=Path("data/raw/th422bg4yd-1.zip"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/iari_wheat_224"))
    parser.add_argument("--size", type=int, default=224)
    args = parser.parse_args(); print(prepare(args.archive, args.output, args.size))


if __name__ == "__main__":
    main()
