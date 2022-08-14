import sys

# Usage: update.py <file.cpp> <file.meta.json>
# Marks a meta file as stale.

if __name__ == '__main__':
    cpp_file = sys.argv[1]
    meta_file = sys.argv[2]

    # Mark file as stale
    with open(meta_file, 'w') as f:
        f.write(f'{{"filename": "{cpp_file}", "stale": true}}')
