import os
import subprocess
import json
from typing import Callable, List, Dict, Tuple


def _default_logger(text: str, tag=None):
    print(text, end='')


def _is_windows_no_window():
    creationflags = 0
    startupinfo = None
    if os.name == 'nt':
        if hasattr(subprocess, 'CREATE_NO_WINDOW'):
            creationflags = subprocess.CREATE_NO_WINDOW
        else:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            startupinfo = si
    return creationflags, startupinfo


def get_video_duration(file_path: str, logger: Callable = None, timeout: int = 10) -> float:
    """Return duration in seconds for a single video using ffprobe."""
    logger = logger or _default_logger
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            file_path
        ]

        creationflags, startupinfo = _is_windows_no_window()
        if startupinfo:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, startupinfo=startupinfo)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, creationflags=creationflags)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            return duration
        else:
            logger(f"  ⚠ Error processing {os.path.basename(file_path)}\n")
            return 0.0

    except subprocess.TimeoutExpired:
        logger(f"  ⚠ Timeout processing {os.path.basename(file_path)}\n")
        return 0.0
    except FileNotFoundError:
        logger("\n❌ ERROR: ffprobe not found. Please install FFmpeg:\n")
        logger("   Windows: Download from https://ffmpeg.org/download.html\n")
        logger("   Mac: brew install ffmpeg\n")
        logger("   Linux: sudo apt install ffmpeg\n\n")
        raise
    except Exception as e:
        logger(f"  ⚠ Error processing {os.path.basename(file_path)}: {e}\n")
        return 0.0


def calculate_total_duration_in_folder(folder_path: str,
                                       video_extensions: List[str],
                                       cancel_check: Callable[[], bool] = lambda: False,
                                       logger: Callable = None) -> Tuple[float, int]:
    """Return (total_duration_seconds, video_count) in the folder."""
    logger = logger or _default_logger
    total_duration = 0.0
    video_count = 0

    try:
        for filename in os.listdir(folder_path):
            if cancel_check():
                return total_duration, video_count

            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in video_extensions):
                duration = get_video_duration(file_path, logger=logger)
                total_duration += duration
                video_count += 1
                logger(f"  ✓ {filename}: {duration/60:.2f} min\n")
    except Exception as e:
        logger(f"  ⚠ Error scanning folder {folder_path}: {e}\n")

    return total_duration, video_count


def traverse_and_calculate(root_folder: str,
                           video_extensions: List[str],
                           cancel_check: Callable[[], bool] = lambda: False,
                           logger: Callable = None) -> Tuple[List[Dict], float, int]:
    """Traverse root_folder, calculate durations per folder and return summaries.

    Returns: (folder_summaries, grand_total_seconds, total_videos)
    folder_summaries: list of dicts with keys: path, name, minutes
    """
    logger = logger or _default_logger

    grand_total_duration = 0.0
    total_videos = 0
    folder_summaries: List[Dict] = []

    logger("=" * 80 + "\n", None)
    logger("VIDEO DURATION ANALYSIS\n", None)
    logger("=" * 80 + "\n\n", None)

    for dirpath, dirnames, filenames in os.walk(root_folder):
        if cancel_check():
            logger("\n⚠ Processing stopped by user\n", None)
            return folder_summaries, grand_total_duration, total_videos

        has_videos = any(f.lower().endswith(tuple(video_extensions)) for f in filenames)
        if has_videos:
            logger(f"\n📁 {dirpath}\n", None)
            logger("-" * 80 + "\n", None)

            total_duration, video_count = calculate_total_duration_in_folder(dirpath, video_extensions, cancel_check=cancel_check, logger=logger)

            if cancel_check():
                logger("\n⚠ Processing stopped by user\n", None)
                return folder_summaries, grand_total_duration, total_videos

            total_videos += video_count
            total_duration_minutes = total_duration / 60
            total_duration_hours = total_duration / 3600

            logger(f"\n  Folder Summary:\n", None)
            logger(f"  • Videos: {video_count}\n", None)
            logger(f"  • Duration: {total_duration:.2f} sec | {total_duration_minutes:.2f} min | {total_duration_hours:.2f} hrs\n", None)

            grand_total_duration += total_duration

            folder_summaries.append({
                'path': dirpath,
                'name': os.path.basename(dirpath) or dirpath,
                'minutes': total_duration_minutes
            })

    if not cancel_check():
        grand_total_minutes = grand_total_duration / 60
        grand_total_hours = grand_total_duration / 3600

        logger("\n" + "=" * 80 + "\n", None)
        logger("FINAL REPORT\n", None)
        logger("=" * 80 + "\n\n", None)

        for i, folder in enumerate(folder_summaries, 1):
            logger(f"{folder['name']}: {folder['minutes']:.2f} min\n", None)

        logger("\n" + "-" * 80 + "\n", None)
        logger(f"TOTAL: {grand_total_minutes:.2f} min ({grand_total_hours:.2f} hours)\n", None)
        logger("=" * 80 + "\n", None)

    return folder_summaries, grand_total_duration, total_videos
