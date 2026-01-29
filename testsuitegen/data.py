import os


def write_files_to_txt(root_dir, output_file):
    with open(output_file, "w", encoding="utf-8") as outfile:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip specified folders
            for folder in ["models", "sample_applications", "artifacts"]:
                if folder in dirnames:
                    dirnames.remove(folder)

            for filename in filenames:
                # Skip specified files
                if filename in ["data.py", "cli.py", "test.py", "test.yaml", ".env", '.gitignore', 'all_files_content.txt']:
                    continue

                # Filter files by extension or specific names
                if filename.endswith((".py", ".json")) or filename in [
                    "README.md",
                    "requirements.txt",
                ]:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        # Try reading the file with utf-8 encoding
                        with open(file_path, "r", encoding="utf-8") as infile:
                            content = infile.read()
                    except UnicodeDecodeError:
                        # If utf-8 fails, fall back to latin-1 encoding
                        try:
                            with open(file_path, "r", encoding="latin-1") as infile:
                                content = infile.read()
                        except Exception as e:
                            print(f"Error reading file {file_path}: {e}")
                            continue
                    # Write to the output file in the specified format
                    outfile.write("======================\n\n")
                    outfile.write(f"{file_path}\n\n")
                    outfile.write(f"{content}\n\n")
                    outfile.write("==============================\n\n")


if __name__ == "__main__":
    root_directory = "./"
    output_file_path = os.path.join(root_directory, "all_files_content.txt")
    write_files_to_txt(root_directory, output_file_path)
    print(f"All file contents have been written to {output_file_path}")
