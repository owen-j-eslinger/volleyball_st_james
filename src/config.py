import sys
import os
from pathlib import Path

def setup_project_environment(markers={'Data', 'src', '.git'}):
    """
    Locates the project root by searching upwards from this file's directory,
    then configures the system path and working directory.
    """
    # Start the search from the directory where this config.py file is stored
    current_dir = Path(__file__).resolve().parent
    found_root = None

    # Search upwards to the filesystem root
    for candidate in [current_dir] + list(current_dir.parents):
        if any((candidate / m).exists() for m in markers):
            found_root = candidate
            break

    # Fallback to environment variable if markers are not found
    if not found_root:
        env_fallback = os.getenv("PROJECT_ROOT_FALLBACK")
        if env_fallback and Path(env_fallback).exists():
            found_root = Path(env_fallback)

    if found_root:
        root_str = str(found_root)
        os.chdir(root_str)
        
        # Add project root to sys.path if not already present
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
            
        return found_root
    else:
        raise RuntimeError(
            f"Could not find project root starting from: {current_dir}"
        )

# Execute environment setup upon import
PROJECT_ROOT = setup_project_environment()
