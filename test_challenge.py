import copy
import unittest
from evaluate_challenge import evaluate_cases
from search import SearchIndex


class ChallengeTests(unittest.TestCase):
    def setUp(self):
        self.index = SearchIndex([{'source': 'memory.md#chunk-1', 'text': 'memory limit'},
                                  {'source': 'rollback.md#chunk-1', 'text': 'release rollback'}])
        self.cases = [{'id': 'positive', 'category': 'relevant', 'query': 'memory', 'expected_source': 'memory.md'},
                      {'id': 'negative', 'category': 'irrelevant', 'query': 'weather', 'expected_source': None}]

    def test_relevant_metrics_exclude_negative_cases(self):
        result = evaluate_cases(self.index, self.cases)['overall']
        self.assertEqual(result['hit_rate_at_3'], 1)
        self.assertEqual(result['mean_reciprocal_rank_at_3'], 1)
        self.assertEqual(result['correct_abstention_rate'], 1)

    def test_lexical_overlap_is_counted_as_false_positive(self):
        self.cases[1]['query'] = 'camera memory card'
        result = evaluate_cases(self.index, self.cases)['overall']
        self.assertEqual(result['irrelevant_query_false_positive_rate'], 1)
        self.assertEqual(result['correct_abstention_rate'], 0)

    def test_undefined_metrics_are_null(self):
        result = evaluate_cases(self.index, self.cases[1:])['overall']
        self.assertIsNone(result['hit_rate_at_3'])
        self.assertIsNone(result['mean_reciprocal_rank_at_3'])

    def test_empty_dataset_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_cases(self.index, [])

    def test_duplicate_id_rejected(self):
        self.cases[1]['id'] = self.cases[0]['id']
        with self.assertRaises(ValueError):
            evaluate_cases(self.index, self.cases)

    def test_missing_label_is_not_silently_negative(self):
        del self.cases[1]['expected_source']
        with self.assertRaises(ValueError):
            evaluate_cases(self.index, self.cases)

    def test_unknown_source_rejected(self):
        self.cases[0]['expected_source'] = 'typo.md'
        with self.assertRaises(ValueError):
            evaluate_cases(self.index, self.cases)

    def test_category_breakdown_and_input_immutability(self):
        before = copy.deepcopy(self.cases)
        result = evaluate_cases(self.index, self.cases)
        self.assertEqual(result['by_category']['irrelevant']['queries'], 1)
        self.assertEqual(self.cases, before)


if __name__ == '__main__':
    unittest.main()
