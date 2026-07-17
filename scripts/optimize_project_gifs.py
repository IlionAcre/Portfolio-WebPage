"""One-off maintenance script: re-encode project GIFs to WebP where it actually helps.

Run this after updating a project's GIF on S3 and pulling it locally (start
the app once so data.py downloads the current GIFs into
static/generated/projects/, then run this script). It re-encodes each GIF to
lossy WebP (quality=75) and keeps the result only if it's smaller than the
original - some of these GIFs are already small/simple enough that WebP's
overhead makes them bigger, so those are left alone.

Usage: uv run --with pillow python scripts/optimize_project_gifs.py

Qualifying WebP files are written to static/optimized_projects/ and are
committed as regular tracked files - data.py prefers them over fetching the
raw GIF from S3 when present. This intentionally does not run automatically:
committing the result is a manual step so changes to the served assets are
visible in git history.
"""
import os
from PIL import Image

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(SCRIPT_DIR, "..", "static", "generated", "projects")
DEST_DIR = os.path.join(SCRIPT_DIR, "..", "static", "optimized_projects")


def convert_one(gif_path, webp_path):
    im = Image.open(gif_path)
    n_frames = getattr(im, "n_frames", 1)

    frames = []
    durations = []
    for i in range(n_frames):
        im.seek(i)
        frames.append(im.convert("RGBA").copy())
        durations.append(im.info.get("duration", 100))

    os.makedirs(DEST_DIR, exist_ok=True)
    tmp_path = webp_path + ".tmp"
    frames[0].save(
        tmp_path,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        quality=75,
        method=4,
    )

    gif_size = os.path.getsize(gif_path)
    webp_size = os.path.getsize(tmp_path)

    if webp_size < gif_size:
        os.replace(tmp_path, webp_path)
        return gif_size, webp_size, True
    else:
        os.remove(tmp_path)
        return gif_size, webp_size, False


def main():
    if not os.path.isdir(SOURCE_DIR):
        print(f"No {SOURCE_DIR} found - run the app once first so it downloads the GIFs from S3.")
        return

    gif_files = sorted(f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".gif"))
    if not gif_files:
        print(f"No GIFs found in {SOURCE_DIR}.")
        return

    print(f"{'file':<10} {'gif':>10} {'webp':>10} {'result'}")
    for fname in gif_files:
        project_id = fname.rsplit(".", 1)[0]
        gif_path = os.path.join(SOURCE_DIR, fname)
        webp_path = os.path.join(DEST_DIR, f"{project_id}.webp")

        # Remove any stale optimized version before re-checking, so a GIF that
        # no longer benefits doesn't leave an outdated WebP behind.
        if os.path.exists(webp_path):
            os.remove(webp_path)

        gif_size, webp_size, kept = convert_one(gif_path, webp_path)
        result = f"kept ({100 * webp_size // gif_size}%)" if kept else "skipped, GIF is smaller"
        print(f"{project_id:<10} {gif_size/1024/1024:>8.2f}MB {webp_size/1024/1024:>8.2f}MB  {result}")

    print(f"\nDone. Optimized files are in {os.path.normpath(DEST_DIR)} - commit them along with this run.")


if __name__ == "__main__":
    main()
