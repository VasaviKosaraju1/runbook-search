/* BM25 retrieval for the static demo. No API keys, uploads, or model calls. */
(function (root) {
  'use strict';
  function tokenize(text) {
    return text.toLowerCase().match(/[a-z0-9]+/g) || [];
  }
  class SearchIndex {
    constructor(documents) {
      this.documents = documents;
      this.terms = documents.map(document => {
        const counts = new Map();
        tokenize(document.text).forEach(word => counts.set(word, (counts.get(word) || 0) + 1));
        return counts;
      });
      this.lengths = this.terms.map(terms => [...terms.values()].reduce((a, b) => a + b, 0));
      this.average = this.lengths.reduce((a, b) => a + b, 0) / Math.max(documents.length, 1);
      this.frequency = new Map();
      this.terms.forEach(terms => terms.forEach((_, word) => {
        this.frequency.set(word, (this.frequency.get(word) || 0) + 1);
      }));
    }
    search(query, limit = 3) {
      if (!Number.isInteger(limit) || limit < 1 || limit > 100) {
        throw new RangeError('limit must be between 1 and 100');
      }
      const words = new Set(tokenize(query));
      const results = [];
      this.documents.forEach((document, i) => {
        let score = 0;
        words.forEach(word => {
          const count = this.terms[i].get(word) || 0;
          if (!count) return;
          const df = this.frequency.get(word);
          const idf = Math.log(1 + (this.documents.length - df + 0.5) / (df + 0.5));
          const norm = 1.2 * (1 - 0.75 + 0.75 * this.lengths[i] / this.average);
          score += idf * count * 2.2 / (count + norm);
        });
        if (score > 0) results.push({...document, score: Number(score.toFixed(6))});
      });
      return results.sort((a, b) => b.score - a.score || (a.source < b.source ? -1 : a.source > b.source ? 1 : 0)).slice(0, limit);
    }
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {SearchIndex, tokenize};
  else root.RunbookSearch = {SearchIndex, tokenize};
})(typeof globalThis !== 'undefined' ? globalThis : this);
