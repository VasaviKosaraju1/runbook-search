"""Build the public demo dataset from this repository's synthetic runbooks."""
import json
from pathlib import Path
from search import load_documents


def build(folder):
    folder = Path(folder)
    documents = load_documents(folder)
    output = folder / 'runbooks.json'
    output.write_text(json.dumps(documents, indent=2) + '\n', encoding='utf-8')
    return documents


if __name__ == '__main__':
    documents = build(Path(__file__).parent)
    print(f'Built runbooks.json with {len(documents)} synthetic document chunks.')
