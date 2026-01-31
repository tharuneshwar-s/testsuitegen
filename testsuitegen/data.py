import os
from pathlib import Path

# Configurable lists for including/excluding files and directories
INCLUDE_FILES = [
    "*.py",
    "*.json",
    "README.md",
    "requirements.txt",
    "*.ts",
    "*.js",
    "*.tsx",
    "*.md",
    "*.txt",
    "*.yml",
    "*.yaml",
    "*.env",
    "*.config.*",
    "*.lock",
    "package.json",
    "tsconfig.json",
    "pyproject.toml",
    "setup.py",
    "Makefile",
    "Dockerfile",
    "*.dockerfile",
    "*.sh",
    "*.bat",
    "*.ps1",
]

EXCLUDE_FILES = [
    "data.py",
    "cli.py",
    "test.py",
    "test.yaml",
    ".env",
    ".gitignore",
    "all_data.txt",
    "all_files_content.txt",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "Thumbs.db",
    "*.log",
    "*.tmp",
    "*.swp",
    "*.bak",
    "*.old",
    "node_modules",
    ".git",
    ".vscode",
    ".idea",
    "build",
    "dist",
    "*.egg-info",
    ".pytest_cache",
    ".coverage",
    "htmlcov",
    ".tox",
    ".mypy_cache",
    ".dmypy.json",
    "dmypy.json",
]

INCLUDE_DIRECTORIES = [
    "backend",
    "frontend",
    "testsuitegen",
    "tmp",
    ".",
]

EXCLUDE_DIRECTORIES = [
    "models",
    "sample_applications",
    "artifacts",
    "__pycache__",
    "node_modules",
    ".git",
    ".vscode",
    ".idea",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "htmlcov",
    ".coverage",
    "logs",
]

def should_include_file(filename, filepath):
    """Check if file should be included based on include/exclude lists."""
    # Check exclude files first
    if any(filename == exclude or filename.endswith(exclude.lstrip("*")) for exclude in EXCLUDE_FILES):
        return False

    # Check include patterns
    for include in INCLUDE_FILES:
        if include.startswith("*"):
            if filename.endswith(include[1:]):
                return True
        elif filename == include:
            return True

    return False

def should_include_directory(dirname, dirpath):
    """Check if directory should be included."""
    # Exclude specific directories
    if dirname in EXCLUDE_DIRECTORIES:
        return False

    # Include specific directories or all if INCLUDE_DIRECTORIES contains "."
    if "." in INCLUDE_DIRECTORIES or dirname in INCLUDE_DIRECTORIES:
        return True

    return False

def write_files_to_txt(root_dir, output_file):
    """Write all included files to a text file in the specified format."""
    root_path = Path(root_dir)

    with open(output_file, "w", encoding="utf-8") as outfile:
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Filter directories
            dirnames[:] = [d for d in dirnames if should_include_directory(d, dirpath)]

            for filename in filenames:
                filepath = Path(dirpath) / filename

                if should_include_file(filename, filepath):
                    try:
                        # Try reading the file with utf-8 encoding
                        with open(filepath, "r", encoding="utf-8") as infile:
                            content = infile.read()
                    except UnicodeDecodeError:
                        # If utf-8 fails, fall back to latin-1 encoding
                        try:
                            with open(filepath, "r", encoding="latin-1") as infile:
                                content = infile.read()
                        except Exception as e:
                            print(f"Error reading file {filepath}: {e}")
                            continue

                    # Write to the output file in the specified format
                    outfile.write("====================\n")
                    outfile.write(f"path: {filepath}\n\n")
                    outfile.write(f"{content}\n")
                    outfile.write("===========================\n\n")

if __name__ == "__main__":
    root_directory = "."
    output_file_path = os.path.join(root_directory, "all_data.txt")
    write_files_to_txt(root_directory, output_file_path)
    print(f"All file contents have been written to {output_file_path}")