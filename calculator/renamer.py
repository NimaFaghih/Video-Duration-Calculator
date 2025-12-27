import os
import re
from typing import Callable, List, Dict, Tuple


def _default_logger(text: str, tag=None):
    print(text, end='')


def rename_folders_with_duration(folder_summaries: List[Dict], logger: Callable = None) -> Tuple[List[Dict], Dict]:
    """Rename folders by appending "(NN min)". Returns (rename_history, summary_counts)."""
    logger = logger or _default_logger

    rename_history = []
    renamed_count = 0
    skipped_count = 0
    error_count = 0

    logger("\n" + "=" * 80 + "\n", None)
    logger("RENAMING FOLDERS\n", None)
    logger("=" * 80 + "\n\n", None)

    for folder_data in folder_summaries:
        old_path = folder_data['path']
        old_name = folder_data['name']
        minutes = folder_data['minutes']

        if re.search(r'\(\d+(\.\d+)?\s*min\)', old_name):
            logger(f"⏭ Skipped (already has duration): {old_name}\n", None)
            skipped_count += 1
            continue

        new_name = f"{old_name} ({minutes:.0f} min)"
        parent_dir = os.path.dirname(old_path)
        new_path = os.path.join(parent_dir, new_name)

        try:
            os.rename(old_path, new_path)
            rename_history.append({
                'old_path': old_path,
                'new_path': new_path,
                'old_name': old_name,
                'new_name': new_name
            })
            logger(f"✓ Renamed: {old_name}\n", None)
            logger(f"       → {new_name}\n\n", None)
            renamed_count += 1
        except Exception as e:
            logger(f"❌ Error renaming {old_name}: {str(e)}\n\n", None)
            error_count += 1

    logger("-" * 80 + "\n", None)
    logger("RENAME SUMMARY:\n", None)
    logger(f"✓ Successfully renamed: {renamed_count}\n", None)
    if skipped_count > 0:
        logger(f"⏭ Skipped: {skipped_count}\n", None)
    if error_count > 0:
        logger(f"❌ Errors: {error_count}\n", None)
    logger("=" * 80 + "\n", None)

    summary = {
        'renamed': renamed_count,
        'skipped': skipped_count,
        'errors': error_count
    }

    return rename_history, summary


def revert_renames(rename_history: List[Dict], logger: Callable = None) -> Dict:
    logger = logger or _default_logger

    logger("\n" + "=" * 80 + "\n", None)
    logger("REVERTING RENAMES\n", None)
    logger("=" * 80 + "\n\n", None)

    reverted = 0
    skipped = 0
    errors = 0

    for entry in reversed(rename_history):
        old_path = entry['old_path']
        new_path = entry['new_path']
        old_name = entry['old_name']
        new_name = entry['new_name']

        if os.path.exists(new_path) and not os.path.exists(old_path):
            try:
                os.rename(new_path, old_path)
                logger(f"✓ Reverted: {new_name}\n", None)
                logger(f"       → {old_name}\n\n", None)
                reverted += 1
            except Exception as e:
                logger(f"❌ Error reverting {new_name}: {str(e)}\n\n", None)
                errors += 1
        elif os.path.exists(old_path):
            logger(f"⏭ Skipped (original exists): {old_name}\n", None)
            skipped += 1
        else:
            logger(f"⚠ Missing: {new_name} (cannot revert)\n", None)
            errors += 1

    logger("-" * 80 + "\n", None)
    logger("REVERT SUMMARY:\n", None)
    logger(f"✓ Successfully reverted: {reverted}\n", None)
    if skipped > 0:
        logger(f"⏭ Skipped: {skipped}\n", None)
    if errors > 0:
        logger(f"❌ Errors: {errors}\n", None)
    logger("=" * 80 + "\n", None)

    return {'reverted': reverted, 'skipped': skipped, 'errors': errors}
