import os
import shutil
import tempfile
from git import Repo

def clone_repo(repo_url: str) -> str:
    """Clones a GitHub repository to a temporary directory and returns the path."""
    if not repo_url.startswith(("http://", "https://")):
        raise ValueError("Invalid repository URL. Must start with http:// or https://")
    if " " in repo_url or ";" in repo_url:
        raise ValueError("Invalid characters in repository URL.")
        
    temp_dir = tempfile.mkdtemp()
    try:
        Repo.clone_from(repo_url, temp_dir, depth=1)
        return temp_dir
    except Exception as e:
        shutil.rmtree(temp_dir)
        raise e

def cleanup_repo(repo_path: str):
    """Removes the cloned repository from the temporary directory."""
    if os.path.exists(repo_path):
        import stat
        def remove_readonly(func, path, excinfo):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(repo_path, onerror=remove_readonly)
