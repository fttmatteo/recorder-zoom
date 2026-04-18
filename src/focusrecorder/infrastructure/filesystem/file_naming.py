from pathlib import Path


def get_next_filename(output_dir: Path | str, prefix: str = "video", extension: str = ".mp4") -> str:
    output_dir = Path(output_dir)
    idx = 1
    while True:
        name = output_dir / f"{prefix}_{idx}{extension}"
        if not name.exists():
            return str(name)
        idx += 1
