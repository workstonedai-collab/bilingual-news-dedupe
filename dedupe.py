"""Conservative, offline duplicate detection for small bilingual news batches."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "source"}
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:\.\d+)?%?")
LATIN = re.compile(r"[a-z0-9]{2,}")
HAN = re.compile(r"[\u4e00-\u9fff]")


def canonical_url(value: str) -> str:
    """Remove fragments and common tracking parameters, preserving content queries."""
    parsed = urlsplit(value.strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        return ""
    try:
        port = parsed.port
    except ValueError:
        return ""
    host = parsed.hostname.casefold()
    if ":" in host:
        host = f"[{host}]"
    default_port = (parsed.scheme.lower(), port) in {("http", 80), ("https", 443)}
    authority = host + (f":{port}" if port and not default_port else "")
    query = urlencode(
        sorted(
            (key, item)
            for key, item in parse_qsl(parsed.query, keep_blank_values=True)
            if not key.casefold().startswith("utm_") and key.casefold() not in TRACKING_KEYS
        )
    )
    return urlunsplit((parsed.scheme.lower(), authority, parsed.path.rstrip("/") or "/", query, ""))


def _tokens(text: str) -> set[str]:
    lowered = text.casefold()
    latin = set(LATIN.findall(lowered))
    han = "".join(HAN.findall(lowered))
    return latin | {han[i : i + 2] for i in range(len(han) - 1)}


def _numbers(title: str) -> set[str]:
    return set(NUMBER.findall(title))


def _published(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except ValueError as exc:
        raise ValueError(f"published_at must be ISO 8601: {value!r}") from exc


def _simhash(text: str) -> int:
    features = _tokens(text)
    if not features:
        return 0
    vector = [0] * 64
    for feature in features:
        digest = int.from_bytes(hashlib.blake2b(feature.encode(), digest_size=8).digest(), "big")
        for bit in range(64):
            vector[bit] += 1 if digest & (1 << bit) else -1
    return sum(1 << bit for bit, score in enumerate(vector) if score >= 0)


def validate_record(record: object, line: int) -> dict:
    if not isinstance(record, dict):
        raise ValueError(f"line {line}: expected a JSON object")
    for field in ("id", "title", "url", "published_at"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f"line {line}: {field} must be a non-empty string")
    for field in ("snippet", "region"):
        if field in record and not isinstance(record[field], str):
            raise ValueError(f"line {line}: {field} must be a string")
    if not canonical_url(record["url"]):
        raise ValueError(f"line {line}: url must be an absolute HTTP(S) URL")
    _published(record["published_at"])
    return record


def match(left: dict, right: dict, max_hours: int = 72) -> tuple[str, float] | None:
    """Return a reason and confidence proxy, or None when evidence is insufficient."""
    if _numbers(left["title"]) and _numbers(right["title"]):
        if _numbers(left["title"]) != _numbers(right["title"]):
            return None
    if left.get("region") and right.get("region") and left["region"] != right["region"]:
        return None
    if canonical_url(left["url"]) == canonical_url(right["url"]):
        return ("canonical_url", 1.0)
    hours = abs((_published(left["published_at"]) - _published(right["published_at"])).total_seconds()) / 3600
    if hours > max_hours:
        return None
    a, b = _tokens(left["title"]), _tokens(right["title"])
    if not a or not b:
        return None
    similarity = len(a & b) / len(a | b)
    if similarity >= 0.72:
        return ("title_similarity", round(similarity, 3))
    distance = bin(_simhash(left["title"] + " " + left.get("snippet", "")) ^ _simhash(right["title"] + " " + right.get("snippet", ""))).count("1")
    if similarity >= 0.48 and distance <= 9:
        return ("title_and_simhash", round(similarity, 3))
    return None


def dedupe(records: list[dict]) -> dict:
    """Preserve order and every input record; duplicates are reported, never deleted."""
    unique: list[dict] = []
    duplicates: list[dict] = []
    seen_ids: set[str] = set()
    for line, raw in enumerate(records, 1):
        item = validate_record(raw, line)
        if item["id"] in seen_ids:
            raise ValueError(f"line {line}: duplicate id {item['id']!r}")
        seen_ids.add(item["id"])
        found = next(((kept, result) for kept in unique if (result := match(kept, item))), None)
        if found:
            kept, (reason, score) = found
            duplicates.append({"item": item, "duplicate_of": kept["id"], "reason": reason, "score": score})
        else:
            unique.append(item)
    return {"unique": unique, "duplicates": duplicates, "input_count": len(records)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline duplicate report for JSONL news items")
    parser.add_argument("input", type=Path, help="UTF-8 JSONL file")
    parser.add_argument("--output", type=Path, help="write JSON report here instead of stdout")
    args = parser.parse_args(argv)
    try:
        lines = args.input.read_text(encoding="utf-8").splitlines()
        records = [json.loads(line) for line in lines if line.strip()]
        report = dedupe(records)
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
