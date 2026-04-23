from docx import Document
from docxcompose.composer import Composer
import sys
import os

def merge_docs(output_name, file_list):
    print(f"Merging {len(file_list)} files into {output_name}...")
    master = Document(file_list[0])
    composer = Composer(master)
    for filename in file_list[1:]:
        print(f"Appending {filename}...")
        doc = Document(filename)
        composer.append(doc)
    composer.save(output_name)
    print(f"Merged into {output_name}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python merge.py <output_file> <input_file1> <input_file2> ...")
        sys.exit(1)
    
    output_file = sys.argv[1]
    input_files = sys.argv[2:]
    
    # Ensure all input files exist
    for f in input_files:
        if not os.path.exists(f):
            print(f"Error: {f} not found.")
            sys.exit(1)

    merge_docs(output_file, input_files)
