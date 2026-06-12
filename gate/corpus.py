"""Corpus loading. Posts are markdown files with YAML frontmatter."""

import os
import re
from dataclasses import dataclass

import yaml


@dataclass
class Post:
    slug: str
    title: str
    primary_keyword: str
    cluster_id: str
    content_class: str  # pillar | mid | programmatic
    body: str
    path: str

    @property
    def word_count(self) -> int:
        return len(re.findall(r"\b\w+\b", self.body))


def parse_markdown(path: str) -> Post:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    meta, body = {}, raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
    slug = meta.get("slug") or os.path.splitext(os.path.basename(path))[0]
    return Post(
        slug=slug,
        title=meta.get("title", slug),
        primary_keyword=meta.get("primary_keyword", ""),
        cluster_id=str(meta.get("cluster_id", "")),
        content_class=meta.get("content_class", "mid"),
        body=body,
        path=path,
    )


def load_corpus(directory: str):
    posts = []
    for name in sorted(os.listdir(directory)):
        if name.endswith(".md"):
            posts.append(parse_markdown(os.path.join(directory, name)))
    return posts
