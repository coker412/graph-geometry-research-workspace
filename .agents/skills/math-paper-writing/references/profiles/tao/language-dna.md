# Language DNA: the selected Tao corpus

Twenty sole-authored papers, 715 PDF pages. Eighteen are research papers/notes; T18 and T20 are explicitly expository surveys. T19 is an early reformulation paper. The selection deliberately spans geometry, PDE, harmonic analysis, combinatorics, number theory and operator theory; it is not a random sample of Tao's output or solely his latest period. See the [twenty-source index](structure-patterns.md#source-index) and [source records](sources.json).

## Computed observations

[Statistics](statistics.json) use PDF blocks with at least twelve English word tokens and at least 65% alphabetic characters as a prose proxy. References are excluded after their heading; T05/T14 contain publisher-template artifacts, and many PDFs have imperfect formula/ligature extraction. Do not treat the following as clean manuscript measurements.

| Quantity | Median across papers | Range across papers |
| --- | ---: | ---: |
| Words per extracted sentence | 19.91 | 17.16–25.49 |
| Characters per extracted sentence | 116.75 | 101.78–162.01 |
| Sentences per prose-like block | 1.98 | 1.53–3.02 |
| Fraction with at least 50 characters | 0.82 | 0.75–0.91 |

The at-most-15-character fraction has median 0.01 (range 0.00–0.03). Sentence candidates require at least three English tokens; all material after the first References heading is excluded, including any later appendix. Extracted opening parentheses total 6,318; Unicode em dashes total zero, which may reflect encoding. Neither is a recommendation about punctuation. Heading-length and part-of-speech estimates are not reliable enough to support rules; candidate headings were inspected separately rather than treated as a validated heading corpus.

Frequent content tokens include `theorem` (1,091), `smooth` (468), `case` (434), `time` (405), and `function` (387). Qualifying/connecting phrases include `in particular` (238), `on the other hand` (61), `more precisely` (59), `informally` (39), and `heuristic` (31 substring matches). These are raw counts, not length-normalized style scores.

## Language decisions supported by reading

T01 labels a probability heuristic and follows it with a precise statement. T13 explicitly marks its scaling discussion as non-rigorous. T16 says which errors are temporarily suppressed in its outline. The useful trait is control of logical status, not a preference for the word “heuristic.”

T05 and T17 explain why the imported language fits the obstacle. T09 and T12 qualify what their constructions leave unresolved. These qualifications carry mathematical information and should survive polishing.

Different topics, genres, page counts and PDF encodings confound comparisons of extracted sentence averages. Do not lengthen sentences to sound like Tao. T07's eleven-page construction also prevents treating long introductions as an author-wide requirement.
