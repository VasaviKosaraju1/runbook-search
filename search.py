"""Local BM25 retrieval baseline for operational runbooks. Python 3.11+."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re
import sys


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


class SearchIndex:
    def __init__(self, documents):
        self.documents = documents
        self.terms = [Counter(tokenize(d['text'])) for d in documents]
        self.lengths = [sum(t.values()) for t in self.terms]
        self.average = sum(self.lengths) / max(len(self.lengths), 1)
        self.frequency = Counter(word for terms in self.terms for word in terms)

    def search(self, query, limit=3):
        if not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError('limit must be between 1 and 100')
        results = []
        for doc, terms, length in zip(self.documents, self.terms, self.lengths):
            score = 0.0
            for word in set(tokenize(query)):
                count = terms[word]
                if not count:
                    continue
                df = self.frequency[word]
                idf = math.log(1 + (len(self.documents) - df + 0.5) / (df + 0.5))
                norm = 1.2 * (1 - 0.75 + 0.75 * length / self.average)
                score += idf * count * 2.2 / (count + norm)
            if score > 0:
                results.append({**doc, 'score': round(score, 6)})
        return sorted(results, key=lambda d: (-d['score'], d['source']))[:limit]


def load_documents(folder):
    if not Path(folder).is_dir():
        raise ValueError('docs must point to an existing directory')
    documents = []
    for path in sorted(Path(folder).glob('runbook-*.md')):
        for number, paragraph in enumerate(path.read_text(encoding='utf-8').split('\n\n'), 1):
            if paragraph.strip():
                documents.append({'source': f'{path.relative_to(folder)}#chunk-{number}',
                                  'text': paragraph.strip()})
    return documents


def evaluate(index, cases):
    if not cases:
        raise ValueError('evaluation cases cannot be empty')
    hits, reciprocal = 0, 0.0
    for case in cases:
        results = index.search(case['query'])
        rank = next((i for i, result in enumerate(results, 1)
                     if result['source'].split('#')[0] == case['expected_source']), None)
        hits += rank is not None
        reciprocal += 1 / rank if rank else 0
    return {'queries': len(cases), 'hit_rate_at_3': hits / len(cases),
            'mean_reciprocal_rank_at_3': reciprocal / len(cases)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', nargs='?', default='')
    parser.add_argument('--docs', default='.')
    parser.add_argument('--evaluate', metavar='JSON_FILE')
    args = parser.parse_args()
    try:
        index = SearchIndex(load_documents(args.docs))
        if args.evaluate:
            output = evaluate(index, json.loads(Path(args.evaluate).read_text()))
        else:
            output = index.search(args.query)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(output, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
