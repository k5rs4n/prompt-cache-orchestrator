#!/usr/bin/env python3
"""
Prompt Cache Compiler
======================
Compiles raw instructions into 3-tier prefix-cache optimized prompts for LLM sub-agents.
Ensures byte-for-byte consistency on static prefixes, checks token thresholds, and eliminates cache misses.
"""

import argparse
import hashlib
import os
import sys
from typing import List, Optional, Tuple

CACHE_STATIC_START = "# [CACHE-STATIC-PREFIX: DO NOT MODIFY]"
CACHE_STATIC_END = "# [/CACHE-STATIC-PREFIX]"
STABLE_CONTEXT_START = "# [STABLE-CONTEXT]"
STABLE_CONTEXT_END = "# [/STABLE-CONTEXT]"
DYNAMIC_TASK_START = "# [DYNAMIC-TASK]"
DYNAMIC_TASK_END = "# [/DYNAMIC-TASK]"


def estimate_tokens(text: str) -> int:
    """
    Estimates token count using character/word heuristics.
    Roughly 4 characters or ~0.75 words per token.
    """
    words = len(text.split())
    chars = len(text)
    # Heuristic blend: avg of chars/4 and words*1.3
    return int((chars / 4.0 + words * 1.3) / 2.0)


def extract_static_prefix(template_content: str) -> str:
    """Extracts the static prefix block from a template file."""
    start_idx = template_content.find(CACHE_STATIC_START)
    end_idx = template_content.find(CACHE_STATIC_END)
    if start_idx != -1 and end_idx != -1:
        return template_content[start_idx : end_idx + len(CACHE_STATIC_END)].strip()
    return template_content.strip()


def hash_prefix(prefix_text: str) -> str:
    """Computes SHA-256 hash of the normalized static prefix."""
    # Normalize CRLF to LF for consistent cross-platform hashing
    normalized = prefix_text.replace("\r\n", "\n").strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()[:12]


def build_context_block(file_paths: List[str]) -> str:
    """Reads and formats target files into a stable context block."""
    context_parts = [STABLE_CONTEXT_START, "Target Files and Context:"]
    for path in file_paths:
        if not os.path.exists(path):
            context_parts.append(f"\n--- File: {path} (NOT FOUND) ---")
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            ext = os.path.splitext(path)[1].lstrip(".") or "txt"
            context_parts.append(f"\nPath: {path}\n```{ext}\n{content}\n```")
        except Exception as e:
            context_parts.append(f"\nPath: {path} (Error reading: {e})")
    context_parts.append(STABLE_CONTEXT_END)
    return "\n".join(context_parts)


def build_dynamic_task(
    title: str,
    task_description: str,
    constraints: Optional[str] = None,
    output_format: Optional[str] = None,
) -> str:
    """Formats the ephemeral dynamic task strictly at the end."""
    parts = [
        DYNAMIC_TASK_START,
        f"GÖREV / TASK: {title}",
        f"DETAY / DESCRIPTION: {task_description}",
    ]
    if constraints:
        parts.append(f"KISITLAR / CONSTRAINTS:\n{constraints}")
    if output_format:
        parts.append(f"BEKLENEN ÇIKTI / OUTPUT FORMAT:\n{output_format}")
    else:
        parts.append(
            "BEKLENEN ÇIKTI / OUTPUT FORMAT: Yalnızca ilgili kod diff'lerini veya değiştirilen fonksiyonları, kısa bir açıklama ile sunun."
        )
    parts.append(DYNAMIC_TASK_END)
    return "\n".join(parts)


def compile_prompt(
    template_path: str,
    file_paths: List[str],
    task_title: str,
    task_description: str,
    constraints: Optional[str] = None,
    output_format: Optional[str] = None,
) -> Tuple[str, dict]:
    """Compiles the full 3-tier prompt and returns metadata."""
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        template_raw = f.read()

    static_prefix = extract_static_prefix(template_raw)
    context_block = build_context_block(file_paths)
    dynamic_task = build_dynamic_task(task_title, task_description, constraints, output_format)

    # Normalize newlines
    full_prompt = f"{static_prefix}\n\n{context_block}\n\n{dynamic_task}"

    prefix_hash = hash_prefix(static_prefix)
    prefix_tokens = estimate_tokens(static_prefix)
    total_tokens = estimate_tokens(full_prompt)

    metadata = {
        "prefix_hash": prefix_hash,
        "prefix_tokens_est": prefix_tokens,
        "total_tokens_est": total_tokens,
        "cache_ready": prefix_tokens >= 1024,
        "warning": (
            None
            if prefix_tokens >= 1024
            else f"Prefix tokens ({prefix_tokens}) below recommended 1024 token cache threshold."
        ),
    }

    return full_prompt, metadata


def main():
    parser = argparse.ArgumentParser(
        description="Compile and verify prefix-cache optimized sub-agent prompts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Compile command
    compile_parser = subparsers.add_parser("compile", help="Compile a 3-tier prompt")
    compile_parser.add_argument("--template", "-t", required=True, help="Path to markdown template")
    compile_parser.add_argument(
        "--files", "-f", nargs="*", default=[], help="Target files for stable context"
    )
    compile_parser.add_argument("--title", required=True, help="Short task title")
    compile_parser.add_argument("--task", "-d", required=True, help="Detailed task description")
    compile_parser.add_argument("--constraints", "-c", help="Specific task constraints")
    compile_parser.add_argument("--output", "-o", help="Write compiled prompt to file")

    # Hash command
    hash_parser = subparsers.add_parser("hash", help="Compute prefix hash to verify determinism")
    hash_parser.add_argument("--template", "-t", required=True, help="Path to markdown template")

    args = parser.parse_args()

    if args.command == "hash":
        with open(args.template, "r", encoding="utf-8") as f:
            content = f.read()
        prefix = extract_static_prefix(content)
        h = hash_prefix(prefix)
        tok = estimate_tokens(prefix)
        print(f"Prefix Hash: {h}")
        print(f"Estimated Tokens: {tok}")
        print(f"Meets 1024-token cache threshold: {'YES' if tok >= 1024 else 'NO'}")

    elif args.command == "compile":
        compiled, meta = compile_prompt(
            template_path=args.template,
            file_paths=args.files,
            task_title=args.title,
            task_description=args.task,
            constraints=args.constraints,
        )

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(compiled)
            print(f"Compiled prompt saved to: {args.output}")
        else:
            print("--- COMPILED PROMPT ---")
            print(compiled)
            print("-----------------------")

        print("\n[PROMPT METADATA]")
        print(f"Prefix Hash: {meta['prefix_hash']}")
        print(f"Prefix Tokens (Est): {meta['prefix_tokens_est']}")
        print(f"Total Tokens (Est): {meta['total_tokens_est']}")
        print(f"Cache Ready: {meta['cache_ready']}")
        if meta["warning"]:
            print(f"WARNING: {meta['warning']}")


if __name__ == "__main__":
    main()
