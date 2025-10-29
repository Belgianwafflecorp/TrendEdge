import json
import logging
from pathlib import Path
from typing import Iterable, Set


ROOT = Path(__file__).resolve().parents[1]
logger = logging.getLogger(__name__)


def _ensure_dir(folder_name: str) -> Path:
    d = ROOT / folder_name
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_list_to(folder_name: str, var_name: str, data: Iterable) -> Path:
    """Save an iterable of items as a sorted JSON list into <folder_name>/<var_name>.json.

    Returns the path written.
    """
    out_dir = _ensure_dir(folder_name)
    serializable = sorted(list(data))
    out_path = out_dir / f"{var_name}.json"
    with out_path.open("w", encoding="utf8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)
    logger.info("Wrote %d items to %s", len(serializable), out_path)
    return out_path


def load_list_from(folder_name: str, var_name: str) -> Set[str]:
    """Load list JSON from <folder_name>/<var_name>.json and return a set of items."""
    path = ROOT / folder_name / f"{var_name}.json"
    with path.open(encoding="utf8") as f:
        data = json.load(f)
    logger.info("Loaded %d items from %s", len(data), path)
    return set(data)
