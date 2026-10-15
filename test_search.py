import unittest
import tempfile
from pathlib import Path
from search import SearchIndex, load_documents, evaluate

class SearchTests(unittest.TestCase):
    def setUp(self):
        self.index = SearchIndex(load_documents(Path(__file__).parent))
    def test_relevant_runbook_is_first(self):
        self.assertTrue(self.index.search('OOMKilled memory')[0]['source'].startswith('runbook-memory.md'))
    def test_unknown_query_has_no_results(self):
        self.assertEqual(self.index.search('xyzunseen'), [])
    def test_empty_index(self):
        self.assertEqual(SearchIndex([]).search('memory'), [])
    def test_empty_query(self):
        self.assertEqual(self.index.search(''), [])
    def test_limit(self):
        with self.assertRaises(ValueError): self.index.search('memory', 0)
    def test_tie_breaking_is_deterministic(self):
        index=SearchIndex([{'source':'b','text':'same'},{'source':'a','text':'same'}])
        self.assertEqual(index.search('same')[0]['source'],'a')
    def test_metrics(self):
        result=evaluate(self.index,[{'query':'memory','expected_source':'runbook-memory.md'}])
        self.assertEqual(result['mean_reciprocal_rank_at_3'],1)
    def test_missing_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError): load_documents(str(Path(folder) / 'missing'))
    def test_file_is_not_a_docs_directory(self):
        with self.assertRaises(ValueError): load_documents(Path(__file__).with_name('evaluation.json'))
    def test_empty_directory_is_valid(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(load_documents(folder), [])
    def test_empty_evaluation_rejected(self):
        with self.assertRaises(ValueError): evaluate(self.index,[])

if __name__ == '__main__': unittest.main()
