"""Unified sync and optimization pipeline for portfolio projects and assets.

Run this script to:
1. Optimize any raw GIFs/images dropped into `media_inbox/` (or specified via --media).
   - Resizes frames to fit carousel card bounds (default max-width 640px).
   - Encodes to lossy animated WebP (quality=75) preserving frame timing.
   - Automatically updates `data/projects.json` with the new asset path.
2. Validate local `data/projects.json` and `data/skills.json`.
3. Back up remote S3 content and upload the fresh JSONs and optimized media.
4. Trigger `/admin/refresh` on production so changes appear instantly without redeploying.

Usage:
  uv run python scripts/sync.py
  uv run python scripts/sync.py --media my_demo.gif --project 1
  uv run python scripts/sync.py --skip-s3
  uv run python scripts/sync.py --dry-run
"""
import argparse
import json
import logging
import os
import shutil
import urllib.error
import urllib.request
import boto3
from dotenv import load_dotenv
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("sync")

load_dotenv()

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "data")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
SKILLS_FILE = os.path.join(DATA_DIR, "skills.json")
MEDIA_INBOX = os.path.join(REPO_ROOT, "media_inbox")
OPTIMIZED_DIR = os.path.join(REPO_ROOT, "static", "optimized_projects")
BACKUP_DIR = os.path.join(REPO_ROOT, "data_backup")

MAX_WIDTH = 640
WEBP_QUALITY = 75


def get_s3_client():
    key_id = os.getenv("KEY_ID")
    access_key = os.getenv("ACCESS_KEY")
    region = os.getenv("REGION")
    bucket = os.getenv("BUCKET")

    if not all([key_id, access_key, region, bucket]):
        return None, None

    client = boto3.client(
        "s3",
        aws_access_key_id=key_id,
        aws_secret_access_key=access_key,
        region_name=region,
    )
    return client, bucket


def optimize_image_or_animation(src_path, dest_path, max_width=MAX_WIDTH, quality=WEBP_QUALITY):
    """Resize and compress an image or animated GIF/WebP using Pillow."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    orig_size = os.path.getsize(src_path)

    with Image.open(src_path) as im:
        n_frames = getattr(im, "n_frames", 1)
        frames = []
        durations = []

        resample_filter = getattr(Image.Resampling, "LANCZOS", Image.LANCZOS)

        for i in range(n_frames):
            im.seek(i)
            frame = im.convert("RGBA")
            w, h = frame.size
            if w > max_width:
                new_h = int(h * (max_width / w))
                frame = frame.resize((max_width, new_h), resample=resample_filter)
            frames.append(frame)
            durations.append(im.info.get("duration", 100))

        tmp_path = dest_path + ".tmp"
        if n_frames > 1:
            frames[0].save(
                tmp_path,
                format="WEBP",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                quality=quality,
                method=5,
            )
        else:
            frames[0].save(tmp_path, format="WEBP", quality=quality, method=5)

    new_size = os.path.getsize(tmp_path)
    os.replace(tmp_path, dest_path)
    savings = (1 - (new_size / orig_size)) * 100 if orig_size > 0 else 0
    return orig_size, new_size, savings


def match_project(file_stem, projects):
    """Attempt to match a file name to a project by numeric ID or title keyword."""
    # 1. Direct ID match: "1.gif", "project_2", etc.
    digits = "".join(ch for ch in file_stem if ch.isdigit())
    if digits:
        proj_id = int(digits)
        for p in projects:
            if p["id"] == proj_id:
                return p

    # 2. Keyword match: "culprit.gif", "marketmood.webp"
    clean_stem = file_stem.lower().replace("_", " ").replace("-", " ")
    for p in projects:
        title_lower = p["title"].lower()
        if clean_stem in title_lower or any(part in title_lower for part in clean_stem.split()):
            return p

    return None


def process_inbox(projects, dry_run=False):
    """Scan media_inbox/ for raw assets, optimize them, and update projects."""
    if not os.path.isdir(MEDIA_INBOX):
        return []

    valid_exts = {".gif", ".png", ".jpg", ".jpeg", ".webp"}
    raw_files = [
        f for f in os.listdir(MEDIA_INBOX)
        if os.path.splitext(f)[1].lower() in valid_exts
    ]

    if not raw_files:
        return []

    processed = []
    logger.info("Found %d media file(s) in %s", len(raw_files), MEDIA_INBOX)

    for fname in raw_files:
        src_path = os.path.join(MEDIA_INBOX, fname)
        file_stem, _ = os.path.splitext(fname)
        matched_proj = match_project(file_stem, projects)

        if not matched_proj:
            logger.warning("Skipping %s: no matching project found in data/projects.json", fname)
            continue

        out_name = f"{matched_proj['id']}.webp"
        dest_path = os.path.join(OPTIMIZED_DIR, out_name)
        rel_path = f"optimized_projects/{out_name}"

        if dry_run:
            logger.info("[DRY RUN] Would optimize %s -> %s (matches project #%s: %s)", fname, rel_path, matched_proj["id"], matched_proj["title"])
            continue

        orig_size, new_size, savings = optimize_image_or_animation(src_path, dest_path)
        logger.info(
            "Optimized %s -> %s (%.2f MB -> %.2f MB, %.1f%% reduction)",
            fname,
            out_name,
            orig_size / (1024 * 1024),
            new_size / (1024 * 1024),
            savings,
        )

        matched_proj["image"] = rel_path
        logger.info("Updated project #%d (%s) image to %s", matched_proj["id"], matched_proj["title"], rel_path)

        # Move raw file to backup/archive instead of deleting
        archive_dir = os.path.join(REPO_ROOT, "data_backup", "raw_media")
        os.makedirs(archive_dir, exist_ok=True)
        shutil.move(src_path, os.path.join(archive_dir, fname))

        processed.append(dest_path)

    return processed


def validate_data():
    with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
        projects = json.load(f)
    with open(SKILLS_FILE, "r", encoding="utf-8") as f:
        skills = json.load(f)

    for p in projects:
        assert "id" in p and "title" in p and "description" in p, f"Invalid project: {p}"
    for s in skills:
        assert "name" in s and "type" in s, f"Invalid skill: {s}"

    return projects, skills


def empty_bucket(s3, bucket):
    """Delete all objects from the S3 bucket."""
    logger.info("Emptying S3 bucket %s...", bucket)
    paginator = s3.get_paginator("list_objects_v2")
    deleted_count = 0
    for page in paginator.paginate(Bucket=bucket):
        objects = [{"Key": obj["Key"]} for obj in page.get("Contents", [])]
        if objects:
            s3.delete_objects(Bucket=bucket, Delete={"Objects": objects})
            deleted_count += len(objects)
    logger.info("Emptied bucket %s (deleted %d objects)", bucket, deleted_count)


def upload_to_s3(s3, bucket, projects, skills, uploaded_assets):
    # Backup remote files first
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for key in ("data/projects.json", "data/skills.json"):
        try:
            body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
            bak_path = os.path.join(BACKUP_DIR, os.path.basename(key) + ".bak")
            with open(bak_path, "wb") as f:
                f.write(body)
        except Exception as e:
            logger.warning("Could not backup remote %s: %s", key, e)

    # Upload projects.json and skills.json
    s3.put_object(
        Bucket=bucket,
        Key="data/projects.json",
        Body=json.dumps(projects, indent=2).encode("utf-8"),
        ContentType="application/json",
    )
    s3.put_object(
        Bucket=bucket,
        Key="data/skills.json",
        Body=json.dumps(skills, indent=2).encode("utf-8"),
        ContentType="application/json",
    )
    logger.info("Uploaded data/projects.json and data/skills.json to S3 bucket %s", bucket)

    # Upload SVG icons from data/icons/ to images/
    icons_dir = os.path.join(DATA_DIR, "icons")
    if os.path.isdir(icons_dir):
        for icon_name in os.listdir(icons_dir):
            if icon_name.endswith(".svg"):
                icon_path = os.path.join(icons_dir, icon_name)
                s3_key = f"images/{icon_name}"
                with open(icon_path, "rb") as f:
                    s3.put_object(
                        Bucket=bucket,
                        Key=s3_key,
                        Body=f.read(),
                        ContentType="image/svg+xml",
                    )
        logger.info("Uploaded SVG icons to s3://%s/images/", bucket)

    # Upload all optimized project media to S3
    if os.path.isdir(OPTIMIZED_DIR):
        for fname in os.listdir(OPTIMIZED_DIR):
            if fname.endswith(".webp"):
                asset_path = os.path.join(OPTIMIZED_DIR, fname)
                s3_key = f"optimized_projects/{fname}"
                with open(asset_path, "rb") as f:
                    s3.put_object(
                        Bucket=bucket,
                        Key=s3_key,
                        Body=f.read(),
                        ContentType="image/webp",
                    )
                logger.info("Uploaded %s to s3://%s/%s", fname, bucket, s3_key)


def trigger_refresh(refresh_url):
    token = os.getenv("REFRESH_TOKEN")
    if not token:
        logger.warning("REFRESH_TOKEN not set in environment; skipping live reload.")
        return

    url = f"{refresh_url.rstrip('/')}/admin/refresh"
    req = urllib.request.Request(
        url,
        data=b"",
        headers={"X-Refresh-Token": token, "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            logger.info("Triggered live refresh at %s: %s", url, data)
    except urllib.error.URLError as e:
        logger.warning("Failed to ping /admin/refresh at %s: %s", url, e)


def main():
    parser = argparse.ArgumentParser(description="Synchronize portfolio projects, skills, and preview assets.")
    parser.add_argument("--media", help="Optional path to a single media file to optimize and attach.")
    parser.add_argument("--project", type=int, help="Project ID for the --media file.")
    parser.add_argument("--empty-bucket", action="store_true", help="Empty the S3 bucket before uploading fresh content.")
    parser.add_argument("--skip-s3", action="store_true", help="Skip S3 upload (local optimization only).")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without modifying files or S3.")
    parser.add_argument("--refresh-url", default=os.getenv("REFRESH_URL", "https://falcontreras.com"), help="URL of running web app to trigger /admin/refresh.")
    args = parser.parse_args()

    projects, skills = validate_data()
    modified_assets = []

    # Handle explicit single-media flag
    if args.media:
        if not os.path.exists(args.media):
            raise FileNotFoundError(f"Media file not found: {args.media}")
        proj_id = args.project or 1
        matched = next((p for p in projects if p["id"] == proj_id), None)
        out_name = f"{proj_id}.webp"
        dest = os.path.join(OPTIMIZED_DIR, out_name)
        rel_path = f"optimized_projects/{out_name}"

        if not args.dry_run:
            orig_sz, new_sz, sav = optimize_image_or_animation(args.media, dest)
            logger.info("Optimized %s -> %s (%.2f MB -> %.2f MB, %.1f%% reduction)", args.media, out_name, orig_sz / (1024*1024), new_sz / (1024*1024), sav)
            if matched:
                matched["image"] = rel_path
            modified_assets.append(dest)
        else:
            logger.info("[DRY RUN] Would optimize %s -> %s", args.media, rel_path)

    # Process any items dropped in media_inbox
    inbox_processed = process_inbox(projects, dry_run=args.dry_run)
    modified_assets.extend(inbox_processed)

    # Save updated projects.json if modified
    if not args.dry_run and (args.media or inbox_processed):
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=2)
        logger.info("Saved updated projects metadata to %s", PROJECTS_FILE)

    if args.skip_s3:
        logger.info("Skipped S3 upload as requested (--skip-s3).")
        return

    s3, bucket = get_s3_client()
    if not s3:
        logger.warning("AWS credentials not configured in .env. Skipping S3 upload.")
        return

    if not args.dry_run:
        if args.empty_bucket:
            empty_bucket(s3, bucket)
        upload_to_s3(s3, bucket, projects, skills, modified_assets)
        if args.refresh_url:
            trigger_refresh(args.refresh_url)
    else:
        if args.empty_bucket:
            logger.info("[DRY RUN] Would empty S3 bucket %s", bucket)
        logger.info("[DRY RUN] Would upload projects.json, skills.json, and %d assets to S3", len(modified_assets))

    logger.info("Sync completed successfully!")


if __name__ == "__main__":
    main()
