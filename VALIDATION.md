# Validation

## Python and HTTP tests

```text
test_blank_query_rejected (test_app.HttpTests) ... ok
test_dataset_is_generated_from_repository_fixtures (test_app.HttpTests) ... ok
test_demo_html (test_app.HttpTests) ... ok
test_health (test_app.HttpTests) ... ok
test_invalid_limits (test_app.HttpTests) ... ok
test_long_query_rejected (test_app.HttpTests) ... ok
test_no_match_is_successful_empty_result (test_app.HttpTests) ... ok
test_private_paths_not_served (test_app.HttpTests) ... ok
test_search_returns_source (test_app.HttpTests) ... ok
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
Ran 20 tests in 0.551s

OK
```

## Browser retrieval tests

```text
8 browser retrieval assertions and 6 Python/JavaScript parity cases passed.
```

## Browser checks

The local interface loaded six chunks from three synthetic runbooks. The Memory pressure example returned the runbook-memory.md source and its passage. An unmatched query returned the no-matching-passages message with no result cards.

The local API tests make real HTTP requests on an ephemeral loopback port. The static UI is tested separately; the public Pages deployment does not run the Python API. Scores and results are fixture checks, not evidence of production retrieval quality.

## Public deployment verified October 16 2026

GitHub Pages deployment completed successfully from main. Public URL: https://vasavikosaraju1.github.io/runbook-search/

Verified the HTTPS page loaded six chunks from the three synthetic runbooks. Memory pressure returned runbook-memory.md references, database connections returned runbook-database.md references, and an unmatched query displayed the no-results state with no result cards. The pull request passed all six GitHub checks before merging.

The public site is static; the Python API and health endpoint remain local development features.
