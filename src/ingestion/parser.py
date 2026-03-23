import os
import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.go', '.java'}
EXCLUDED_DIRS = {'node_modules', '.git', '__pycache__', 'dist', 'build'}

def discover_files(repo_path: str) -> List[str]:
    """
    Recursively discovers file paths within a repository, filtering out excluded
    directories and returning only files matching the allowed extensions.
    """
    valid_files = []
    for root, dirs, files in os.walk(repo_path):
        # Exclude directories inline
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith('.')]
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in ALLOWED_EXTENSIONS:
                valid_files.append(os.path.join(root, file))
    return valid_files

def parse_python_file(file_content: str, rel_path: str, repo_id: str) -> List[Dict]:
    import ast
    chunks = []
    lines = file_content.split('\n')
    try:
        tree = ast.parse(file_content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno
                end = node.end_lineno
                if start and end:
                    chunk_text = '\n'.join(lines[start-1:end])
                    chunks.append({
                        "repo_id": repo_id,
                        "file_path": rel_path,
                        "function_name": node.name,
                        "language": "python",
                        "start_line": start,
                        "end_line": end,
                        "chunk_text": chunk_text
                    })
        # If no functions/classes, chunk by file
        if not chunks:
            raise Exception("No functions found")
    except Exception:
        # Fallback to file level
        chunks.append({
            "repo_id": repo_id,
            "file_path": rel_path,
            "function_name": "file_level",
            "language": "python",
            "start_line": 1,
            "end_line": len(lines),
            "chunk_text": file_content[:4000] # Limit size if needed
        })
    return chunks

def parse_generic_file(file_content: str, rel_path: str, repo_id: str, ext: str) -> List[Dict]:
    lines = file_content.split('\n')
    chunks = []
    chunk_size = 100
    for i in range(0, len(lines), chunk_size):
        end = min(i + chunk_size, len(lines))
        chunk_text = '\n'.join(lines[i:end])
        chunks.append({
            "repo_id": repo_id,
            "file_path": rel_path,
            "function_name": "file_level",
            "language": ext[1:],
            "start_line": i + 1,
            "end_line": end,
            "chunk_text": chunk_text
        })
    return chunks

def parse_repo(repo_path: str, repo_id: str) -> List[Dict]:
    files = discover_files(repo_path)
    all_chunks = []
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Failed to read file {file_path}: {e}")
            continue
            
        rel_path = os.path.relpath(file_path, repo_path).replace('\\', '/')
        ext = os.path.splitext(file_path)[1]
        
        if ext == '.py':
            chunks = parse_python_file(content, rel_path, repo_id)
        else:
            chunks = parse_generic_file(content, rel_path, repo_id, ext)
            
        all_chunks.extend(chunks)
        
    return all_chunks
