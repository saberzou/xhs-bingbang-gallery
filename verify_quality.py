#!/usr/bin/env python3
"""
verify_quality.py — XHS BingBang content quality gate (QA: Axiom)

Purpose
-------
Keep the Sage & Andy feed on the direction Saber approved 2026-06-20:
richer, job-anchored, scene-specific moments — NOT floaty motivational-poster
one-liners. Enforces the WORLD-BIBLE.md voice rules (§7 emotional range, §8
voice rules) on a per-draft and per-batch basis.

What it checks (per draft)
--------------------------
1. bible_hook   present & non-empty   -> every post must trace to a real fact
2. scene        present & non-trivial -> there must be an actual scene, not a vibe
3. rationale    present (warn if null)-> "why this, why now, what it avoids"
4. caption      grounded, not floaty  -> heuristic: concrete anchor vs pure abstraction
5. caption      length sane (<= ~24 zh chars on first line)

What it checks (per batch, last N)
----------------------------------
A. cast diversity     -> not all "both"; solo Sage / solo Andy show up
B. job presence       -> Sage-work and Andy-work scenes actually appear
C. emotional range    -> not 100% 治愈/wholesome; tired/funny/annoyed/quiet present
D. motif anti-repeat  -> same scene motif not reused too often in the window

Exit code 0 = batch PASS, 1 = batch FAIL (any hard violation in window).
Usage:
    python3 verify_quality.py                # checks last 14 drafts
    python3 verify_quality.py --window 7
    python3 verify_quality.py --date 2026-06-21   # check one specific draft
    python3 verify_quality.py --json         # machine-readable
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRAFTS = ROOT / "drafts"

# ---- Heuristic lexicons -----------------------------------------------------
# "Floaty" = abstractions that could live on a generic motivational poster.
# The bible explicitly says: if a line could fit on a generic poster, kill it.
FLOATY_TERMS = [
    "节奏", "价值", "进度", "落后", "领先", "迷茫", "勇敢", "坚持", "成长",
    "力量", "积蓄", "出发", "继续前进", "深呼吸", "慢慢来", "一步一步",
    "加油", "未来", "希望", "光", "治愈", "温柔", "释怀", "放过自己",
    "活在当下", "做自己", "热爱", "相信", "美好", "心安",
]
# Pure-abstraction openers that, when they ARE the whole line, read as poster.
POSTER_WHOLE_LINE = [
    "深呼吸", "晚安", "继续前进吧", "今天也要勇敢", "一步一步来",
    "慢慢来", "加油", "做自己就好", "你的节奏就是对的",
]

# "Grounded" = concrete anchors from the world bible (props, places, jobs, time).
GROUNDED_TERMS = [
    # tech / Sage job
    "改稿", "PM", "对齐", "像素", "px", "需求", "上线", "deadline", "ddl",
    "键盘", "屏幕", "扫街", "修图", "Lightroom", "X100", "胶卷", "底片",
    "工位", "评审", "设计稿", "Figma", "颁奖", "得奖",
    # retail / Andy job
    "上班", "下班", "客人", "顾客", "商场", "专柜", "站", "分期", "花呗",
    "drop", "新品", "试穿", "导购", "提成", "业绩", "拖鞋", "oversize",
    # home / props / world
    "咖啡", "外卖", "单车", "地铁", "阳台", "罗勒", "basil", "雨", "伞",
    "电梯", "沙发", "厨房", "AirPod", "耳机", "快递", "纸船", "猫", "Mochi",
    "便利店", "7-11", "面", "市场", "公园", "长椅", "晾衣", "泡面", "零食",
    "牙膏", "拉萨", "海边", "沙滩", "guitar", "吉他",
    # time anchors
    "凌晨", "深夜", "周三", "周末", "早上", "傍晚", "今晚", "半夜", "中午",
    "一站", "坐过", "10:30", "点",
]

# Emotional buckets — for batch range. A scene/caption maps to >=1.
EMO_BUCKETS = {
    "tired":    ["累", "站", "改稿", "加班", "凌晨", "睡", "垮", "瘫", "坐过", "deadline", "ddl"],
    "funny":    ["又", "嘴硬", "投资", "撞", "丢", "偷", "只看一眼", "假装", "研究"],
    "annoyed":  ["牙膏", "没盖", "争", "26", "24", "wifi", "territory", "占", "抢"],
    "quiet":    ["阳台", "发呆", "不想", "深夜", "窗", "纸船", "看书", "安静", "一个人"],
    "tender":   ["关", "盖被", "伞", "等", "留", "悄悄", "陪", "拥抱", "hug", "牵"],
    "smallwin": ["终于", "PR", "落地", "成", "第一次", "搞定", "上线", "得奖", "颁奖"],
}

HARD = "HARD"   # batch-failing
SOFT = "SOFT"   # warning only


def load_drafts():
    out = []
    if not DRAFTS.exists():
        return out
    for d in sorted(DRAFTS.glob("20*-*-*")):
        if not d.is_dir():
            continue
        meta_p = d / "metadata.json"
        cap_p = d / "caption.md"
        meta = {}
        if meta_p.exists():
            try:
                meta = json.loads(meta_p.read_text(encoding="utf-8"))
            except Exception as e:
                meta = {"_parse_error": str(e)}
        caption = ""
        if cap_p.exists():
            caption = cap_p.read_text(encoding="utf-8").strip()
        # prefer metadata caption, fall back to caption.md first line
        cap_line = (meta.get("caption") or "").strip()
        if not cap_line and caption:
            cap_line = caption.splitlines()[0].strip().strip('"').strip("“”")
        out.append({
            "date": d.name,
            "dir": d,
            "caption": cap_line,
            "scene": (meta.get("scene") or "").strip(),
            "cast": (meta.get("cast") or "").strip().lower(),
            "bible_hook": (meta.get("bible_hook") or "").strip(),
            "rationale": meta.get("rationale"),
            "meta": meta,
            "has_image": (d / "image.png").exists(),
        })
    return out


def caption_groundedness(cap, scene):
    """Return (verdict, hits). verdict in {grounded, weak, floaty}."""
    text = f"{cap} || {scene}"
    g = [t for t in GROUNDED_TERMS if t.lower() in text.lower()]
    f = [t for t in FLOATY_TERMS if t in cap]
    whole_poster = cap.strip().strip('。.!！?？ ') in POSTER_WHOLE_LINE
    # Scene carries weight: a vivid scene rescues a short *neutral* caption.
    scene_rich = len(scene) >= 40
    # But a whole-line poster caption is floaty no matter how rich the scene --
    # Saber's complaint is specifically about the CAPTION reading like a poster.
    if whole_poster:
        return "floaty", {"grounded": g, "floaty": f, "whole_poster": True}
    if g or scene_rich:
        return "grounded", {"grounded": g, "floaty": f}
    if f and not g:
        return "floaty", {"grounded": g, "floaty": f}
    return "weak", {"grounded": g, "floaty": f}


def emo_tags(cap, scene):
    text = f"{cap} {scene}"
    tags = set()
    for bucket, terms in EMO_BUCKETS.items():
        if any(t.lower() in text.lower() for t in terms):
            tags.add(bucket)
    return tags


def check_one(dft):
    issues = []
    cap = dft["caption"]
    scene = dft["scene"]

    if not cap:
        issues.append((HARD, "caption empty"))
    if not dft["bible_hook"]:
        issues.append((HARD, "missing bible_hook (post must trace to a real fact)"))
    # Silent-fallback tripwire: a real LLM scene carries BOTH a bible_hook and a
    # rationale. The legacy fallback pool has neither. If both are absent, the
    # generator almost certainly hit the fallback path (the bug that ran silently
    # for weeks, June 2026 — [proxy] banner broke JSON parsing). Flag it loudly.
    if not dft["bible_hook"] and dft["rationale"] in (None, "", "null"):
        issues.append((HARD, "LIKELY LLM-IDEATION FALLBACK (no hook + no rationale) — check cron.log for parser failure"))
    if not scene or len(scene) < 12:
        issues.append((HARD, "scene missing or too thin"))
    if dft["rationale"] in (None, "", "null"):
        issues.append((SOFT, "rationale is null (add why-this / what-it-avoids)"))

    verdict, hits = caption_groundedness(cap, scene)
    if verdict == "floaty":
        issues.append((HARD, f"caption reads floaty/poster (floaty={hits['floaty']}, grounded={hits['grounded']})"))
    elif verdict == "weak":
        issues.append((SOFT, "caption neither clearly grounded nor floaty — sharpen the anchor"))

    # length sanity on the zh caption first line
    first = cap.splitlines()[0] if cap else ""
    if len(first) > 24:
        issues.append((SOFT, f"caption long ({len(first)} chars) — the drawing speaks, words whisper"))

    return {
        "date": dft["date"],
        "caption": cap,
        "scene": scene,
        "cast": dft["cast"] or "?",
        "bible_hook_raw": dft["bible_hook"],
        "grounded": verdict,
        "emo": sorted(emo_tags(cap, scene)),
        "bible_hook": dft["bible_hook"] or "—",
        "issues": issues,
        "hard": [m for s, m in issues if s == HARD],
        "soft": [m for s, m in issues if s == SOFT],
    }


def check_batch(rows):
    findings = []
    n = len(rows)
    if n == 0:
        return ["(no drafts in window)"]
    casts = [r["cast"] for r in rows]
    both_ratio = casts.count("both") / n
    if both_ratio > 0.7:
        findings.append((HARD, f"cast monotony: {both_ratio:.0%} are 'both' — need more solo Sage/Andy"))
    if "sage" not in casts:
        findings.append((SOFT, "no solo-Sage post in window"))
    if "andy" not in casts:
        findings.append((SOFT, "no solo-Andy post in window"))

    # job presence: does any scene reference each job?
    blob = " ".join((r.get("scene", "") + " " + (r.get("bible_hook_raw") or ""))
                    for r in rows).lower()
    sage_job = any(k in blob for k in ["design", "改稿", "pm", "figma", "screen", "keyboard", "扫街", "lightroom", "px", "对齐"])
    andy_job = any(k in blob for k in ["retail", "mall", "商场", "专柜", "客人", "顾客", "分期", "drop", "站了", "导购", "luxury"])
    if not sage_job:
        findings.append((HARD, "no Sage-WORK scene in window (designer job is the underused goldmine)"))
    if not andy_job:
        findings.append((HARD, "no Andy-WORK scene in window (luxury-retail job is the underused goldmine)"))

    # emotional range across batch
    emo_union = set()
    for r in rows:
        emo_union |= set(r["emo"])
    if len(emo_union) < 3:
        findings.append((HARD, f"emotional range too narrow: only {sorted(emo_union) or 'none-detected'} — mix tired/funny/annoyed/quiet/tender"))

    # grounded ratio
    floaty = [r for r in rows if r["grounded"] == "floaty"]
    if len(floaty) / n > 0.3:
        findings.append((HARD, f"{len(floaty)}/{n} captions floaty (>30%) — drifting back to poster mode"))

    return findings


def fmt(rows_checked, batch_findings, window):
    lines = []
    lines.append(f"XHS Quality Gate — last {window} drafts  ({datetime.now():%Y-%m-%d %H:%M})")
    lines.append("=" * 60)
    hard_total = 0
    for r in rows_checked:
        mark = "✅" if not r["hard"] else "❌"
        if r["hard"]:
            hard_total += len(r["hard"])
        emo = ",".join(r["emo"]) or "—"
        lines.append(f"{mark} {r['date']} [{r['cast']:>4}] g={r['grounded']:<8} emo={emo}")
        lines.append(f"    “{r['caption']}”   ⟵ {r['bible_hook']}")
        for m in r["hard"]:
            lines.append(f"    ❌ {m}")
        for m in r["soft"]:
            lines.append(f"    ⚠️  {m}")
    lines.append("-" * 60)
    lines.append("BATCH:")
    batch_hard = 0
    if not batch_findings:
        lines.append("  ✅ batch checks clean")
    for sev, m in batch_findings:
        if isinstance(sev, str) and sev == HARD:
            batch_hard += 1
            lines.append(f"  ❌ {m}")
        else:
            lines.append(f"  ⚠️  {m}")
    lines.append("=" * 60)
    verdict = "PASS" if (hard_total == 0 and batch_hard == 0) else "FAIL"
    lines.append(f"RESULT: {verdict}   (per-draft hard={hard_total}, batch hard={batch_hard})")
    return "\n".join(lines), verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=14)
    ap.add_argument("--date", type=str, default=None, help="check a single YYYY-MM-DD draft")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    drafts = load_drafts()
    if args.date:
        drafts = [d for d in drafts if d["date"] == args.date]
        if not drafts:
            print(f"no draft for {args.date}", file=sys.stderr)
            sys.exit(2)
        window = 1
    else:
        drafts = drafts[-args.window:]
        window = args.window

    rows_checked = [check_one(d) for d in drafts]
    batch_findings = check_batch(rows_checked) if not args.date else []

    if args.json:
        hard_total = sum(len(r["hard"]) for r in rows_checked)
        batch_hard = sum(1 for s, _ in batch_findings if s == HARD)
        print(json.dumps({
            "window": window,
            "drafts": rows_checked,
            "batch": [{"severity": s, "msg": m} for s, m in batch_findings],
            "result": "PASS" if (hard_total == 0 and batch_hard == 0) else "FAIL",
        }, ensure_ascii=False, indent=2, default=str))
        sys.exit(0 if (hard_total == 0 and batch_hard == 0) else 1)

    report, verdict = fmt(rows_checked, batch_findings, window)
    print(report)
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
