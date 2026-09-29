# 中英文资讯去重工具 | Bilingual News Dedupe

同一条资讯可能带着不同的跟踪参数、链接或改写标题进入素材池；只按标题删除，又可能误伤更新了数字的报道。这个离线 Python 工具帮助编辑、研究和数据团队**先找出可能重复的中英文条目，再决定如何处理**。它保留全部输入，并输出每组匹配的依据。

The same story may enter a feed under different URLs, tracking parameters, or rewritten headlines. Deleting by title alone can hide an updated figure. This offline Python tool helps editorial, research, and data teams **spot likely duplicates before deciding what to keep**. It preserves every input record and explains each match.

**Read in your language / 选择语言：** [完整中文说明](README.zh-CN.md) · [Full English guide](README.en.md)

## 它如何帮助复核 / How it supports review

| 中文 | English |
| --- | --- |
| **综合多条线索：**清理 URL 跟踪参数，比较中英文标题，同时考虑发布时间和地区；数字冲突会阻止直接归为重复。 | **Combine signals:** normalize tracking parameters, compare Chinese and English titles, and consider time and region; conflicting numbers prevent a direct duplicate match. |
| **给出可解释报告：**结果分为 `unique` 与 `duplicates`，重复候选附带 `duplicate_of`、`reason` 和 `score`，原始记录仍在。 | **Explain each candidate:** the JSON report separates `unique` and `duplicates`, with `duplicate_of`, `reason`, and `score` while retaining the source records. |
| **方便接入现有流程：**读取本地 JSONL，输出 JSON；无第三方依赖，不抓取网页，也不调用模型或外部 API。 | **Fit existing workflows:** read local JSONL and emit JSON without third-party packages, web fetching, a model, or an external API. |

适合入库前的小批量筛查、人工复核队列整理和规则原型验证。近似匹配是候选提示；重要内容仍需人工判断。 / Use it for small-batch intake checks, review queues, and rule prototyping. Similarity is a review signal; important decisions still need a person.

## Try it / 立即试用

Requires Python 3.9+; no third-party packages. / 需要 Python 3.9+，无第三方依赖。

```bash
python3 dedupe.py examples/news.jsonl --output /tmp/news-dedupe-report.json
python3 -m unittest discover -s tests -v
```

示例输入 5 条，报告给出 3 条代表记录和 2 条重复候选；其中一条因规范化 URL 相同而匹配，另一条因标题相似而匹配。 / The five-record sample yields three representative records and two duplicate candidates: one matched by canonical URL and one by title similarity.

```text
cn-2 → cn-1  canonical_url
en-2 → en-1  title_similarity
```

The sample contains fictional `example.*` URLs. No requests are sent to them. / 样本中的 `example.*` 地址均为虚构演示地址，不会发起网络请求。

**License / 许可证：** [Apache-2.0](LICENSE). **Repository / 仓库：** [workstonedai-collab/bilingual-news-dedupe](https://github.com/workstonedai-collab/bilingual-news-dedupe).
