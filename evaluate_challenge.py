"""Evaluate relevant queries and no-answer cases without changing retrieval behavior."""
import argparse
import json
from pathlib import Path
from search import SearchIndex, load_documents


def summarize(rows):
    relevant = [row for row in rows if row['expected_source'] is not None]
    negatives = [row for row in rows if row['expected_source'] is None]
    return {
        'queries': len(rows),
        'relevant_queries': len(relevant),
        'irrelevant_queries': len(negatives),
        'hit_rate_at_3': sum(row['rank'] is not None for row in relevant) / len(relevant) if relevant else None,
        'mean_reciprocal_rank_at_3': sum(1 / row['rank'] if row['rank'] else 0 for row in relevant) / len(relevant) if relevant else None,
        'irrelevant_query_false_positive_rate': sum(bool(row['results']) for row in negatives) / len(negatives) if negatives else None,
        'correct_abstention_rate': sum(not row['results'] for row in negatives) / len(negatives) if negatives else None,
    }


def evaluate_cases(index, cases):
    if not isinstance(cases, list) or not cases:
        raise ValueError('cases must be a nonempty list')
    identifiers = set()
    known_sources = {document['source'].split('#')[0] for document in index.documents}
    # Validate the complete dataset before evaluating any query.
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError('each case must be an object')
        for field in ('id', 'category', 'query'):
            value = case.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f'{field} must be a nonempty string')
        if case['id'] in identifiers:
            raise ValueError('case ids must be unique')
        identifiers.add(case['id'])
        if 'expected_source' not in case:
            raise ValueError('expected_source must be explicit; use null for irrelevant queries')
        expected = case['expected_source']
        if expected is not None and (not isinstance(expected, str) or expected not in known_sources):
            raise ValueError('expected_source must name an indexed runbook or be null')
    rows = []
    for case in cases:
        results = index.search(case['query'], limit=3)
        rank = next((position for position, result in enumerate(results, 1)
                     if result['source'].split('#')[0] == case['expected_source']), None)
        rows.append({**case, 'rank': rank, 'results': results})
    categories = sorted({row['category'] for row in rows})
    return {
        'overall': summarize(rows),
        'by_category': {category: summarize([row for row in rows if row['category'] == category]) for category in categories},
        'per_query': rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docs', type=Path, default=Path(__file__).parent)
    parser.add_argument('--cases', type=Path, default=Path(__file__).with_name('evaluation-challenge.json'))
    args = parser.parse_args()
    try:
        index = SearchIndex(load_documents(args.docs))
        result = evaluate_cases(index, json.loads(args.cases.read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, f'Evaluation error: {error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
