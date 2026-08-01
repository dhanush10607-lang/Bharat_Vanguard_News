import os

root = '.'
skip_dirs = {'node_modules', '.next', 'huggingface_cache', '__pycache__', '.git'}
extensions = {'.py', '.ts', '.tsx', '.js', '.jsx', '.md', '.yaml', '.yml', '.html', '.css', '.txt', '.sql'}

count = 0
for dirpath, dirs, files in os.walk(root):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for fname in files:
        ext = os.path.splitext(fname)[1]
        if ext not in extensions and fname not in {'Makefile', 'env.py'}:
            continue
        fpath = os.path.join(dirpath, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'TruthLens' in content:
                new_content = content.replace('TruthLens AI', 'Bharat Vanguard News (BVN)').replace('TruthLens', 'Bharat Vanguard News')
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {fpath}")
                count += 1
        except Exception as e:
            pass

print(f"Total updated: {count}")
