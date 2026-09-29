# 中英文资讯去重工具

同一条资讯经常以不同链接、跟踪参数或改写标题出现。如果直接删掉“看起来相似”的条目，也可能误伤数字更新或不同地区的报道。这个工具提供一个**可解释的离线预检**：报告哪些条目可能重复、依据是什么，并保留全部原始记录供人工判断。

[English guide](README.en.md) · [双语首页](README.md)

## 适合谁

- 维护中英文资讯订阅、研究素材池或人工复核队列的团队。
- 需要在入库前做小批量去重，又不希望引入服务和外部 API 的开发者。
- 想看到“为什么被判为重复”，而不是只得到一个删除后的列表的人。

## 30 秒开始

需要 Python 3.9 或更新版本，无需安装依赖。在本文件夹执行：

```bash
python3 dedupe.py examples/news.jsonl --output /tmp/news-dedupe-report.json
python3 -m unittest discover -s tests -v
```

也可以省略 `--output`，直接把 JSON 报告打印到终端。输出有 `unique`、`duplicates` 和 `input_count` 三部分。每条重复记录会保留完整原文，并说明 `duplicate_of`、`reason` 和 `score`。

```json
{
  "item": {"id": "cn-2", "title": "示例港口一季度吞吐量增长12%：最新统计"},
  "duplicate_of": "cn-1",
  "reason": "canonical_url",
  "score": 1.0
}
```

上面是输出片段；实际 `item` 还包含输入中的其他字段。`score` 是匹配依据的提示值，并非经过校准的概率。

## 输入格式

输入为 UTF-8 JSONL：每行一个 JSON 对象。必填字段如下：

| 字段 | 说明 |
| --- | --- |
| `id` | 本批次内唯一的非空字符串 |
| `title` | 资讯标题，可含中文或英文 |
| `url` | 绝对 HTTP(S) 地址，不允许用户凭据 |
| `published_at` | ISO 8601 日期或时间，如 `2026-01-08T09:00:00Z` |
| `snippet` | 可选的摘要，用于辅助 SimHash |
| `region` | 可选的地区标签；两条都填写且不同时，不做近似匹配 |

可参考 [虚构输入样例](examples/news.jsonl)。输入数据只在本机读取；工具不会访问 URL、调用外部服务或修改输入文件。

## 如何判断

1. 先去掉 URL 片段与常见跟踪参数，保留可能决定文章身份的查询参数。
2. 同一规范化 URL 是强线索，但**标题中的数字冲突**会阻止自动归为重复。
3. 不同 URL 的近似匹配还要求发布时间相差不超过 72 小时，并通过地区保护。
4. 英文词与中文二字片段用于标题相似度；边界情况再用标题和摘要的 SimHash 辅助判断。
5. 结果按输入顺序保留第一条为代表，其他条目写入 `duplicates`，不丢弃原始内容。

这是一套保守启发式规则。翻译稿、改写幅度很大的稿件可能漏检；通用标题可能误判。用于自动删除或对外发布前，请结合人工复核。

## 常见用法

```bash
# 将自己的本地 JSONL 文件写成报告
python3 dedupe.py /path/to/news.jsonl --output /tmp/dedupe.json

# 在脚本里复用
python3 -c 'from dedupe import dedupe; print(dedupe([]))'
```

成功返回码为 `0`；输入文件、JSON 或字段不合法时返回 `2`，错误写到标准错误输出。算法为小批量离线检查，近似比较约为 O(n²)；大规模实时流需增加索引、候选召回和人工复核策略。

## 隐私与发布边界

仓库仅含虚构 `example.*` 样本，没有真实新闻全文、账号、密钥、业务日志或采集配置。工具会把输入记录原样写进报告，因此**不要把含私人数据或令牌的报告公开**。它提供重复候选，不判断新闻真假、版权或转载权限。

这是独立项目，不继承原业务仓库历史。代码采用 [Apache-2.0 许可证](LICENSE)；公开仓库位于 [workstonedai-collab/bilingual-news-dedupe](https://github.com/workstonedai-collab/bilingual-news-dedupe)。
