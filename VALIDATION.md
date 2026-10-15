# Validation

Local validation on Python 3.9.6.

## Unit tests

```text
test_empty_directory_is_valid (test_search.SearchTests) ... ok
test_empty_evaluation_rejected (test_search.SearchTests) ... ok
test_empty_index (test_search.SearchTests) ... ok
test_empty_query (test_search.SearchTests) ... ok
test_file_is_not_a_docs_directory (test_search.SearchTests) ... ok
test_limit (test_search.SearchTests) ... ok
test_metrics (test_search.SearchTests) ... ok
test_missing_directory_is_rejected (test_search.SearchTests) ... ok
test_relevant_runbook_is_first (test_search.SearchTests) ... ok
test_tie_breaking_is_deterministic (test_search.SearchTests) ... ok
test_unknown_query_has_no_results (test_search.SearchTests) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.005s

OK
```

## python3 search.py OOMKilled memory limit

Exit status: 0

```json
[
  {
    "source": "runbook-memory.md#chunk-2",
    "text": "An OOMKilled container exceeded its memory limit. Inspect memory usage and recent workload changes. Check for leaks before increasing limits. Compare requests and limits with observed peak usage.",
    "score": 3.581044
  },
  {
    "source": "runbook-memory.md#chunk-1",
    "text": "# Container memory pressure",
    "score": 1.547627
  }
]
```

## python3 search.py --evaluate evaluation.json

Exit status: 0

```json
{
  "queries": 6,
  "hit_rate_at_3": 1.0,
  "mean_reciprocal_rank_at_3": 1.0
}
```

These checks use small synthetic fixtures. They do not establish production readiness or cloud deployment results.
