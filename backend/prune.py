import sys

def prune_ask(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    start_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('@router.post("/ask", response_model=AskResponse'):
            start_idx = i
            break
            
    if start_idx != -1:
        with open(file_path, 'w') as f:
            f.writelines(lines[:start_idx])
            print("Successfully pruned /ask from ask.py")

if __name__ == "__main__":
    prune_ask(sys.argv[1])
