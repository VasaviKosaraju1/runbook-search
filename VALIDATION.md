# Validation

## Challenge evaluation update October 16 2026

Commands run successfully:

```sh
python3 -m unittest -v
node web.test.cjs
python3 evaluate_challenge.py
```

- 28 Python tests passed, including nine real HTTP tests and eight tests for the challenge evaluator.
- Eight JavaScript retrieval assertions and 18 Python/JavaScript parity cases passed.
- The challenge report contains 18 queries: six baseline, six paraphrased, and six irrelevant.
- Baseline and paraphrase groups each returned the expected source for all six cases, with hit rate at three 1.0 and MRR at three 1.0.
- Four of six irrelevant queries returned results, a false-positive rate of 0.667. Two returned no results, a correct-abstention rate of 0.333.

`evaluation-results.json` records every case and result. Its values are observations of the included synthetic fixtures, not general accuracy estimates. The evaluator rejects missing relevance labels, duplicate case identifiers, and source labels that do not exist in the index. Metrics without applicable cases are null.

This change does not alter the retrieval algorithm or the browser interface. It strengthens evaluation and exposes failures caused by lexical overlap.

## Public demo verification

GitHub Pages: https://vasavikosaraju1.github.io/runbook-search/

The HTTPS page loaded six chunks from three synthetic runbooks. Memory pressure returned runbook-memory.md references, database connections returned runbook-database.md references, and an unmatched query displayed the no-results state with no result cards.

The public site is static. The Python API and health endpoint remain local development features. No private documents or model API calls are used.
