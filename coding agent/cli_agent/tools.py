import json
import os
from pathlib import Path


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files under a directory (relative to workspace).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path relative to workspace root.",
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum directory depth to walk (default 2).",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file from the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace root.",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Start line number (1-indexed).",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of lines to read.",
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to workspace root.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write.",
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite if file exists.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "make_dir",
            "description": "Create a directory under the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path relative to workspace root.",
                    }
                },
                "required": ["path"],
            },
        },
    },
]


def _resolve_path(root: Path, user_path: str) -> Path:
    candidate = Path(user_path)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("Path escapes workspace root.")
    return resolved


def _json_result(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=True)


def list_files(workspace_root: Path, path: str | None = None, max_depth: int | None = None) -> str:
    root = workspace_root.resolve()
    target = _resolve_path(root, path or ".")
    max_depth = 2 if max_depth is None else max_depth
    if not target.exists():
        return _json_result({"error": f"Path not found: {path}"})
    if not target.is_dir():
        return _json_result({"error": f"Not a directory: {path}"})

    results: list[str] = []
    base_depth = len(target.parts)
    for dirpath, dirnames, filenames in os.walk(target):
        depth = len(Path(dirpath).parts) - base_depth
        if depth > max_depth:
            dirnames[:] = []
            continue
        rel_dir = Path(dirpath).relative_to(root)
        for name in sorted(dirnames):
            results.append(str(rel_dir / name) + "/")
        for name in sorted(filenames):
            results.append(str(rel_dir / name))
        if len(results) > 200:
            results.append("... (truncated)")
            break

    return _json_result({"result": results})


def read_file(
    workspace_root: Path,
    path: str,
    offset: int | None = None,
    limit: int | None = None,
) -> str:
    root = workspace_root.resolve()
    target = _resolve_path(root, path)
    if not target.exists():
        return _json_result({"error": f"File not found: {path}"})
    if target.is_dir():
        return _json_result({"error": f"Path is a directory: {path}"})

    text = target.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = max((offset or 1) - 1, 0)
    end = start + (limit or len(lines))
    sliced = lines[start:end]
    return _json_result(
        {
            "result": {
                "path": path,
                "offset": start + 1,
                "lines": sliced,
                "total_lines": len(lines),
            }
        }
    )


def write_file(
    workspace_root: Path,
    path: str,
    content: str,
    overwrite: bool | None = None,
) -> str:
    root = workspace_root.resolve()
    target = _resolve_path(root, path)
    if target.exists() and not (overwrite or False):
        return _json_result({"error": f"File exists: {path}. Set overwrite=true to replace."})

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return _json_result({"result": f"Wrote {path} ({len(content)} bytes)."})


def make_dir(workspace_root: Path, path: str) -> str:
    root = workspace_root.resolve()
    target = _resolve_path(root, path)
    target.mkdir(parents=True, exist_ok=True)
    return _json_result({"result": f"Created directory {path}."})


def execute_tool(name: str, arguments: dict, workspace_root: Path) -> str:
    try:
        if name == "list_files":
            return list_files(
                workspace_root=workspace_root,
                path=arguments.get("path"),
                max_depth=arguments.get("max_depth"),
            )
        if name == "read_file":
            return read_file(
                workspace_root=workspace_root,
                path=arguments["path"],
                offset=arguments.get("offset"),
                limit=arguments.get("limit"),
            )
        if name == "write_file":
            return write_file(
                workspace_root=workspace_root,
                path=arguments["path"],
                content=arguments["content"],
                overwrite=arguments.get("overwrite"),
            )
        if name == "make_dir":
            return make_dir(workspace_root=workspace_root, path=arguments["path"])
    except Exception as exc:
        return _json_result({"error": f"{type(exc).__name__}: {exc}"})

    return _json_result({"error": f"Unknown tool: {name}"})
