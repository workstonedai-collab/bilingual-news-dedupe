# 中英文资讯去重工具 | Bilingual News Dedupe

Spot repeated Chinese and English news items before they enter your feed or review queue. This small, offline Python tool combines URL cleanup, title similarity, publication time, region, and a numeric conflict guard. It **reports** possible duplicates while keeping the original records intact.

在资讯进入列表或人工复核队列前，先识别可能重复的中英文稿件。工具离线运行，结合 URL 规范化、标题相似度、发布时间、地区与数字冲突保护；它只生成去重报告，不删除输入。

**Read in your language / 选择语言：** [完整中文说明](README.zh-CN.md) · [Full English guide](README.en.md)

## Try it / 立即试用

Requires Python 3.9+; no third-party packages. / 需要 Python 3.9+，无第三方依赖。

```bash
python3 dedupe.py examples/news.jsonl --output /tmp/news-dedupe-report.json
python3 -m unittest discover -s tests -v
```

The sample contains fictional `example.*` URLs. No requests are sent to them. / 样本中的 `example.*` 地址均为虚构演示地址，不会发起网络请求。

**License / 许可证：** [Apache-2.0](LICENSE). **Repository / 仓库：** [workstonedai-collab/bilingual-news-dedupe](https://github.com/workstonedai-collab/bilingual-news-dedupe).
