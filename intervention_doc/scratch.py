from docx import Document
import math

def split_test():
    input_filepath = r"E:\homer\homerpdf\intervention_doc\Homer_intervention_V2 Final version with picture.docx"
    doc = Document(input_filepath)
    body_elm = doc._body._body
    
    # Keep only paragraph and table elements for counting
    children = [child for child in body_elm if child.tag.endswith(('}p', '}tbl'))]
    total_elements = len(children)
    print(f"Total block elements: {total_elements}")
    
    num_splits = 5
    chunk_size = math.ceil(total_elements / num_splits)
    
    for i in range(num_splits):
        # Open a fresh copy for each split
        split_doc = Document(input_filepath)
        split_body_elm = split_doc._body._body
        split_children = [child for child in split_body_elm if child.tag.endswith(('}p', '}tbl'))]
        
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total_elements)
        
        # We want to keep elements from start_idx to end_idx - 1
        for j, child in enumerate(split_children):
            if j < start_idx or j >= end_idx:
                split_body_elm.remove(child)
                
        output_filepath = f"split_part_{i+1}.docx"
        split_doc.save(output_filepath)
        print(f"Saved {output_filepath}")

if __name__ == "__main__":
    split_test()
