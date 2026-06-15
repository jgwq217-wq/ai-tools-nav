#!/usr/bin/env python3
"""
AI 工具自动发现脚本 — 每周运行，搜索新上线 AI 工具
输出: scripts/_new_tools.md (有发现时写入，无发现则不创建)
"""

import json, os, re, sys, time
from urllib.request import Request, urlopen
from urllib.error import URLError

# ============ 配置 ============
FIRECRAWL_KEY = os.environ.get("FIRECRAWL_API_KEY", "")
SEARCH_QUERIES = [
    "new AI tools launched this week 2026",
    "best new AI tools 2026 must try",
    "新上线 AI 工具 2026 推荐",
    "国产 AI 新工具 2026",
]

HEADERS = {
    "User-Agent": "AI-Tools-Discover/1.0",
    "Content-Type": "application/json",
}


def load_existing_tools():
    """从 index.html 提取已有工具名列表"""
    tools = set()
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
        for m in re.finditer(r"t\('([^']+)'", content):
            tools.add(m.group(1))
    except FileNotFoundError:
        print("⚠️ index.html 未找到", file=sys.stderr)
    return tools


def search_firecrawl(query: str, max_retries=2):
    """使用 Firecrawl Search API 搜索"""
    if not FIRECRAWL_KEY:
        return []

    url = "https://api.firecrawl.dev/v1/search"
    payload = json.dumps({
        "query": query,
        "limit": 10,
        "sources": [{"type": "web"}],
    })

    for attempt in range(max_retries):
        try:
            req = Request(url, data=payload.encode(), headers={
                **HEADERS,
                "Authorization": f"Bearer {FIRECRAWL_KEY}",
            })
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                results = []
                for item in data.get("data", {}).get("web", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", ""),
                    })
                return results
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"  ⚠️ 搜索失败 '{query[:30]}...': {e}", file=sys.stderr)
    return []


def extract_tool_names(results):
    """从搜索结果中提取可能的 AI 工具名"""
    candidates = {}
    known_noise = {
        "youtube", "reddit", "twitter", "github", "linkedin",
        "blog", "news", "home", "about", "login", "sign",
        "best", "top", "new", "free", "ai", "tool", "tools",
        "2025", "2026", "chatgpt", "gpt",
    }

    for r in results:
        title = r["title"]
        desc = r.get("description", "")

        # 从标题中提取可能的工具名（大写开头的词、中文品牌名）
        words = re.findall(r'[A-Z][a-z]{2,}(?:\s?AI|\s?\.ai)?|\b[一-鿿]{2,6}(?:AI|助手|工具|生成|写作|设计|编程|视频|笔记)\b', title)
        for w in words:
            w = w.strip()
            if w.lower() not in known_noise and len(w) >= 2:
                if w not in candidates:
                    candidates[w] = {"source": r["url"], "title": title}
    return candidates


def manual_checklist():
    """内置待关注工具清单 — 定期人工确认是否已公开上线"""
    return [
        ("Sora 2", "OpenAI 视频生成升级版", "视频",
         "https://sora.com", "付费", ["海外"]),
        ("Claude Cowork", "Anthropic 桌面自动化 Agent", "效率",
         "https://claude.ai", "付费", ["海外", "企业级"]),
        ("Pika 2.0", "AI 短视频升级版", "视频",
         "https://pika.art", "免费+付费", ["海外"]),
        ("Grok 3", "xAI 最新推理模型", "大模型",
         "https://grok.com", "免费+付费", ["海外"]),
    ]


def main():
    existing = load_existing_tools()
    print(f"📊 已收录工具: {len(existing)} 个")
    print(f"🔍 搜索新工具...\n")

    all_candidates = {}

    if FIRECRAWL_KEY:
        for q in SEARCH_QUERIES:
            print(f"  📡 搜索: {q[:40]}...")
            results = search_firecrawl(q)
            candidates = extract_tool_names(results)
            for name, info in candidates.items():
                if name not in existing and name not in all_candidates:
                    all_candidates[name] = info
            time.sleep(1)
    else:
        print("  ⚠️ 未配置 FIRECRAWL_API_KEY，跳过在线搜索")
        print("  💡 在仓库 Settings → Secrets → Actions 中添加")

    # 去重已有工具
    new_tools = {k: v for k, v in all_candidates.items() if k not in existing}

    # 手动清单中未收录的
    manual_new = []
    for name, desc, cat, url, price, scenes in manual_checklist():
        if name not in existing:
            manual_new.append((name, desc, cat, url, price, scenes))

    # 输出结果
    if not new_tools and not manual_new:
        print("\n✅ 暂未发现需要新增的工具")
        # 确保不创建 _new_tools.md
        out = "scripts/_new_tools.md"
        if os.path.exists(out):
            os.remove(out)
        return

    lines = [
        "## 🔍 自动发现的候选工具\n",
        f"> 搜索时间: {time.strftime('%Y-%m-%d %H:%M UTC')}  \n",
        f"> 已收录: {len(existing)} 个 | 新候选: {len(new_tools)} 个\n",
        "\n### 来自网络搜索\n",
    ]

    if new_tools:
        lines.append("| 名称 | 来源 |")
        lines.append("|------|------|")
        for name, info in sorted(new_tools.items())[:20]:
            src = info["source"].split("/")[2] if "/" in info["source"] else info["source"]
            lines.append(f"| {name} | [{src}]({info['source']}) |")
    else:
        lines.append("_本次未搜索到新工具_")

    if manual_new:
        lines.append(f"\n### 📋 待确认清单 ({len(manual_new)} 个)\n")
        lines.append("| 名称 | 描述 | 分类 | 价格 |")
        lines.append("|------|------|------|------|")
        for name, desc, cat, url, price, scenes in manual_new:
            lines.append(f"| [{name}]({url}) | {desc} | {cat} | {price} |")

    lines.append(f"\n---\n🤖 由 [auto-discover](https://github.com/jgwq217-wq/ai-tools-nav/actions) 自动生成")

    out_path = "scripts/_new_tools.md"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n📝 发现 {len(new_tools)} 个候选 + {len(manual_new)} 个待确认")
    print(f"💾 结果写入 {out_path}")


if __name__ == "__main__":
    main()
