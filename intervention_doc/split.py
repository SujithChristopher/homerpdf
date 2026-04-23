from docx import Document
import math
import os

def split_docx(input_filepath, num_splits=5):
    if not os.path.exists(input_filepath):
        print(f"File not found: {input_filepath}")
        return

    # First open to count the elements
    doc = Document(input_filepath)
    body_elm = doc._body._body
    
    # Keep only paragraph and table elements for counting and chunking
    children = [child for child in body_elm if child.tag.endswith(('}p', '}tbl'))]
    total_elements = len(children)
    print(f"Total block elements found: {total_elements}")
    
    # Calculate how many elements go into each file
    chunk_size = math.ceil(total_elements / num_splits)

    for i in range(num_splits):
        # Open a fresh copy of the document for each split to preserve styles/formatting
        split_doc = Document(input_filepath)
        split_body_elm = split_doc._body._body
        split_children = [child for child in split_body_elm if child.tag.endswith(('}p', '}tbl'))]
        
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total_elements)
        
        # We want to keep elements from start_idx to end_idx - 1
        for j, child in enumerate(split_children):
            if j < start_idx or j >= end_idx:
                split_body_elm.remove(child)
                
        output_filepath = f"formatted_split_part_{i+1}.docx"
        split_doc.save(output_filepath)
        print(f"Saved {output_filepath}")

if __name__ == "__main__":
    # Replace with your actual file name
    split_docx(r"E:\homer\homerpdf\intervention_doc\Homer_intervention_V2 Final version with picture.docx")