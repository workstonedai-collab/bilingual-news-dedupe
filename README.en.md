# Bilingual News Dedupe

The same story can arrive under different URLs, tracking parameters, and rewritten headlines. Deleting every similar-looking item can also hide a revised figure or a report about another region. This tool provides an **explainable offline preflight**: it reports likely duplicates and their reasons while preserving every original record for review.

[中文说明](README.zh-CN.md) · [Bilingual home](README.md)

## Who it is for

- Teams maintaining Chinese or English news feeds, research collections, or review queues.
- Developers who need small-batch deduplication without a service or external API.
- Reviewers who want to see why two items matched before deciding what to keep.

## Start in 30 seconds

Use Python 3.9 or newer. There are no third-party dependencies. From this folder:

```bash
python3 dedupe.py examples/news.jsonl --output /tmp/news-dedupe-report.json
python3 -m unittest discover -s tests -v
```

Omit `--output` to print the JSON report to the terminal. It contains `unique`, `duplicates`, and `input_count`. Each duplicate entry retains the full input item and records `duplicate_of`, `reason`, and `score`.

```json
{
  "item": {"id": "cn-2", "title": "示例港口一季度吞吐量增长12%：最新统计"},
  "duplicate_of": "cn-1",
  "reason": "canonical_url",
  "score": 1.0
}
```

This is an excerpt; the actual `item` includes all other input fields. `score` is an explanatory matching signal, **not** a calibrated probability.

## Input format

Supply UTF-8 JSONL with one object per line:

| Field | Meaning |
| --- | --- |
| `id` | Nonempty identifier, unique within the batch |
| `title` | Chinese or English headline |
| `url` | Absolute HTTP(S) URL without embedded credentials |
| `published_at` | ISO 8601 date or timestamp, for example `2026-01-08T09:00:00Z` |
| `snippet` | Optional summary, used by SimHash |
| `region` | Optional region label; different supplied labels block approximate matching |

See the [fictional sample input](examples/news.jsonl). The tool reads local files only. It never requests the URLs, calls external services, or changes the input file.

## How matching works

1. Remove URL fragments and common tracking parameters, while preserving query parameters that may identify content.
2. Treat identical canonical URLs as strong evidence, unless headline numbers conflict.
3. For different URLs, require publication times within 72 hours and compatible regions.
4. Compare English words and Chinese character bigrams in headlines; use title-and-summary SimHash for borderline cases.
5. Keep the first item in input order as the representative and report later candidates in `duplicates`.

These are conservative heuristics. Heavily rewritten or translated stories can be missed; generic headlines can be false positives. Review results before automatic deletion or publication.

## Common use

```bash
# Write a report for your own local JSONL file
python3 dedupe.py /path/to/news.jsonl --output /tmp/dedupe.json

# Reuse from Python
python3 -c 'from dedupe import dedupe; print(dedupe([]))'
```

Exit code `0` means success. Invalid input files, JSON, or fields return `2` with a message on standard error. Approximate matching is O(n²) and intended for small offline batches; large live streams need candidate indexing and a review workflow.

## Privacy and release boundary

This package includes only fictional `example.*` samples, with no real article bodies, accounts, keys, logs, or collection configuration. Because the report retains input records, **do not publish reports containing private data or tokens**. This tool does not determine whether content is true, licensed, or permitted to republish.

This standalone project has no business repository history. It is released under the [Apache-2.0 license](LICENSE) at [workstonedai-collab/bilingual-news-dedupe](https://github.com/workstonedai-collab/bilingual-news-dedupe).
