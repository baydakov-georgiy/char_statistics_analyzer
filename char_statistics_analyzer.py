import os
import sys
import argparse
import csv
from collections import defaultdict

config = {
    "default_output_file": "out.csv",
    "replacements": {
        " ": "[space]",
        "\n": "[newline]",
        "\t": "[tab]",
        "\b": "[backspace]",
        ",": "[comma]",
        ';': "[semicolon]"
    }
}

def is_match_extension(file, search_exts, ignore_case=False):
    if (len(file) < 1):
        return False
    file_parts = file.split(".")
    file_ext = file_parts[-1] if len(file_parts) > 1 and len(file_parts[-1]) > 0 else "."
    search_exts = [search_ext[1:] if search_ext[0] == "." and len(search_ext) > 1 else search_ext for search_ext in search_exts]
    if ignore_case:
        file_ext = file_ext.lower()
        search_exts = [search_ext.lower() for search_ext in search_exts]
    return any(file_ext == search_ext for search_ext in search_exts)

def find_files_with_ext(directory, search_exts, ignore_case=False, recursive=False):
    matched_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if is_match_extension(file, search_exts, ignore_case):
                matched_files.append(os.path.join(root, file))
        if not recursive:
            dirs.clear()

    return matched_files

def count_characters_in_file(filepath):
    count = defaultdict(int)
    try:
        with open(filepath, "rb") as file:
            for line in file:
                for char in line.decode("utf-8"):
                    count[char] += 1
    except UnicodeDecodeError:
        print("Error: Could not read file. It may be binary")
        sys.exit(1)
    except Exception as e:
        print(f"Error: file does not open\n{e}")
        sys.exit(1)
    return count

def replace_special_chars(char):
    return config["replacements"].get(char, char if char.isprintable() else f"[0x{ord(char):02x}]")

def create_characters_table(files_data):
    all_chars = set()
    for count in files_data.values():
        all_chars.update(count.keys())

    replaced_chars = sorted(
        [(char, replace_special_chars(char)) for char in all_chars],
        key=lambda x: ord(x[0])
    )

    total_counts = {}
    for char, replaced in replaced_chars:
        total_counts[replaced] = sum(
            count.get(char, 0)
            for count in files_data.values()
        )

    sorted_chars = sorted(
        replaced_chars,
        key=lambda x: -total_counts[x[1]]
    )

    table = []
    columns = ["filepath"] + [replaced for _, replaced in sorted_chars]
    for filepath, count in files_data.items():
        row = {"filepath": filepath}
        for char, replaced in sorted_chars:
            row[replaced] = count.get(char, 0)
        table.append(row)

    total_row = {"filepath": "TOTAL"}
    for char, replaced in sorted_chars:
        total_row[replaced] = total_counts[replaced]
    table.append(total_row)

    return table, columns

def save_to_csv(table, columns, output_file=config["default_output_file"]):
    output_dir = os.path.dirname(output_file)
    if output_dir != '' and not os.path.exists(output_dir):
        print(f"Error: output directory `{output_dir}` does not exist")
        sys.exit(1)
    try:
        with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            writer.writerows(table)
    except Exception as e:
        print(f"Error: file is not saved.\n{e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Counting characters in files with extensions")
    parser.add_argument("directory", help="Directory path to search for files")
    parser.add_argument("-e", "--extensions", nargs="+", required=True, help="Extensions for search")
    parser.add_argument("-o", "--output", nargs="?", required=False, help="Path to output file with result")
    parser.add_argument("-i", "--ignore_case", required=False, action="store_true", help="Ignore case for extensions")
    parser.add_argument("-r", "--recursive", required=False, action="store_true", help="Search extensions inside the specified directory and subdirectories")

    args = parser.parse_args()

    expanded_dir = os.path.expanduser(args.directory)

    if not os.path.isdir(expanded_dir):
        print(f"Error: {expanded_dir} does not directory")
        sys.exit(1)

    print(f"Search files with extensions: {args.extensions}")
    files = find_files_with_ext(args.directory, args.extensions, args.ignore_case, args.recursive)

    if not files:
        print("Files not found")
        sys.exit(1)

    print("Found files:")
    for file in files:
        print(f"    {file}")
    print(f"Analysis {len(files)} files...")
    files_data = {}
    for filepath in files:
        count = count_characters_in_file(filepath)
        if count is not None:
            files_data[filepath] = count
    
    if not files_data:
        print("No data for analysis")
        sys.exit(1)

    output_file = args.output if args.output else config["default_output_file"]
    table, columns = create_characters_table(files_data)
    save_to_csv(table, columns, output_file)

    print(f"Success! Analysis file `{output_file}`")

if __name__ == "__main__":
    main()
