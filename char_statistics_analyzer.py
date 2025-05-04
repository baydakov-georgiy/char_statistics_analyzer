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
        "\b": "[backspace]"
    }
}

def find_files_with_ext(directory, extensions):
    matched_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext.lower()) for ext in extensions):
                matched_files.append(os.path.join(root, file))
    return matched_files

def count_characters_in_file(filepath):
    count = defaultdict(int)
    try:
        with open(filepath, 'r', encoding="utf-8") as file:
            for line in file:
                for char in line:
                    count[char] += 1
    except UnicodeDecodeError:
        print("Error: Could not read file. It may be binary")
        return None
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

    table = []
    columns = ["filepath"] + [replaced for _, replaced in replaced_chars]
    for filepath, count in files_data.items():
        row = {"filepath": filepath}
        for char, replaced in replaced_chars:
            row[replaced] = count.get(char, 0)
        table.append(row)

    return table, columns

def save_to_csv(table, columns, output_file=config["default_output_file"]):
    try:
        with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            writer.writerows(table)
            return True
    except IOError as e:
        print(f"Error: file is not saved.\n{e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Counting characters in files with extensions")
    parser.add_argument("directory", help="Directory path to search for files")
    parser.add_argument("-e", "--extensions", nargs="+", required=True, help="Extensions for search")
    parser.add_argument("-o", "--output", nargs="?", required=False, help="Path to output file with result")

    args = parser.parse_args()

    expanded_dir = os.path.expanduser(args.directory)

    if not os.path.isdir(expanded_dir):
        print(f"Error: {expanded_dir} does not directory")
        sys.exit(1)

    print(f"Search files with extensions: {args.extensions}...")
    files = find_files_with_ext(args.directory, args.extensions)

    if not files:
        print("Files not found")
        sys.exit(1)

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
    save_to_csv(table, columns, output_file);

    print(f"Success! Analysis file `./{output_file}`")

if __name__ == "__main__":
    main()
