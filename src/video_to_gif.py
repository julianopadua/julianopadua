"""
Converts a screen recording to an optimized GIF for GitHub READMEs.

Usage:
    python src/video_to_gif.py [--input assets/demo.mp4] [--fps 10] [--width 800]

Dependencies:
    pip install moviepy
"""

import argparse
import sys
from pathlib import Path

from moviepy.video.io.VideoFileClip import VideoFileClip


SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi"}
OUTPUT_PATH = Path("assets/forest-portal-demo.gif")
DEFAULT_CANDIDATES = [
    Path("assets/demo.mp4"),
    Path("assets/demo.mov"),
    Path("assets/demo.mkv"),
]


def find_input_video() -> Path:
    for candidate in DEFAULT_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"No input video found. Looked for: {[str(p) for p in DEFAULT_CANDIDATES]}\n"
        "Pass an explicit path with --input."
    )


def convert(input_path: Path, output_path: Path, fps: int, max_width: int) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format '{input_path.suffix}'. "
            f"Supported: {SUPPORTED_EXTENSIONS}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with VideoFileClip(str(input_path)) as clip:
        orig_w, orig_h = clip.size
        if orig_w > max_width:
            scale = max_width / orig_w
            new_size = (max_width, int(orig_h * scale))
            clip = clip.resized(new_size)

        effective_fps = min(fps, clip.fps)

        print(
            f"  Input : {input_path} ({orig_w}x{orig_h} @ {clip.fps:.1f} fps)"
        )
        print(
            f"  Output: {output_path} "
            f"({clip.size[0]}x{clip.size[1]} @ {effective_fps} fps)"
        )

        clip.write_gif(
            str(output_path),
            fps=effective_fps,
            logger="bar",
        )

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  Done. File size: {size_mb:.2f} MB")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a screen recording to an optimized GIF."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to the input video file (default: auto-detect in assets/).",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=10,
        help="Target framerate (default: 10).",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=800,
        help="Maximum output width in pixels (default: 800).",
    )
    args = parser.parse_args()

    try:
        input_path = args.input if args.input is not None else find_input_video()
        convert(input_path, OUTPUT_PATH, fps=args.fps, max_width=args.width)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
