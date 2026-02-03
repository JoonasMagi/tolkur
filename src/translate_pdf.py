#!/usr/bin/env python3
"""Translate a foreign-language PDF into Estonian while preserving layout."""
from __future__ import annotations

import argparse
import dataclasses
import os
import time
from typing import Iterable, List, Tuple

import fitz  # PyMuPDF
import requests

LINE_HEIGHT_FACTOR = 1.2


@dataclasses.dataclass
class TranslationConfig:
    endpoint: str
    api_key: str | None
    source_lang: str | None
    target_lang: str
    rate_limit_s: float


@dataclasses.dataclass
class TextBlock:
    page_number: int
    bbox: fitz.Rect
    text: str
    font: str
    font_size: float


def collect_text_blocks(doc: fitz.Document) -> List[TextBlock]:
    blocks: List[TextBlock] = []
    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        text_dict = page.get_text("dict")
        for block in text_dict["blocks"]:
            if block.get("type") != 0:
                continue
            block_text_lines: List[str] = []
            font_name = "helv"
            font_size = 11.0
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                if line_text.strip():
                    block_text_lines.append(line_text)
                for span in line.get("spans", []):
                    if span.get("font"):
                        font_name = span["font"]
                    if span.get("size"):
                        font_size = span["size"]
            block_text = "\n".join(block_text_lines).strip()
            if not block_text:
                continue
            bbox = fitz.Rect(block["bbox"])
            blocks.append(
                TextBlock(
                    page_number=page_index,
                    bbox=bbox,
                    text=block_text,
                    font=font_name,
                    font_size=font_size,
                )
            )
    return blocks


def chunk_text(text: str, limit: int = 4000) -> Iterable[str]:
    current: List[str] = []
    current_len = 0
    for line in text.splitlines():
        if current_len + len(line) + 1 > limit and current:
            yield "\n".join(current)
            current = []
            current_len = 0
        current.append(line)
        current_len += len(line) + 1
    if current:
        yield "\n".join(current)


def break_long_word(word: str, font: str, fontsize: float, max_width: float) -> List[str]:
    if fitz.get_text_length(word, fontname=font, fontsize=fontsize) <= max_width:
        return [word]
    pieces: List[str] = []
    current = ""
    for char in word:
        candidate = f"{current}{char}"
        if fitz.get_text_length(candidate, fontname=font, fontsize=fontsize) > max_width and current:
            pieces.append(current)
            current = char
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces


def wrap_text(text: str, font: str, fontsize: float, max_width: float) -> str:
    wrapped_lines: List[str] = []
    for paragraph in text.splitlines():
        if not paragraph.strip():
            wrapped_lines.append("")
            continue
        current_line = ""
        for word in paragraph.split():
            for piece in break_long_word(word, font, fontsize, max_width):
                candidate = piece if not current_line else f"{current_line} {piece}"
                if fitz.get_text_length(candidate, fontname=font, fontsize=fontsize) <= max_width:
                    current_line = candidate
                else:
                    if current_line:
                        wrapped_lines.append(current_line)
                    current_line = piece
        if current_line:
            wrapped_lines.append(current_line)
    return "\n".join(wrapped_lines)


def fit_text_to_box(
    text: str, font: str, fontsize: float, bbox: fitz.Rect, min_font_size: float = 6.0
) -> Tuple[str, float]:
    size = fontsize
    while size >= min_font_size:
        wrapped = wrap_text(text, font, size, bbox.width)
        line_count = max(1, len(wrapped.splitlines()))
        estimated_height = line_count * size * LINE_HEIGHT_FACTOR
        if estimated_height <= bbox.height:
            return wrapped, size
        size -= 0.5
    return wrap_text(text, font, min_font_size, bbox.width), min_font_size


def translate_text(text: str, config: TranslationConfig) -> str:
    if not text.strip():
        return text
    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    translated_chunks: List[str] = []
    for chunk in chunk_text(text):
        payload = {
            "q": chunk,
            "source": config.source_lang or "auto",
            "target": config.target_lang,
            "format": "text",
        }
        response = requests.post(config.endpoint, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        translated_text = data.get("translatedText") or data.get("translation") or ""
        translated_chunks.append(translated_text)
        if config.rate_limit_s:
            time.sleep(config.rate_limit_s)
    return "\n".join(translated_chunks)


def translate_pdf(input_path: str, output_path: str, config: TranslationConfig) -> None:
    doc = fitz.open(input_path)
    blocks = collect_text_blocks(doc)
    for block in blocks:
        page = doc.load_page(block.page_number)
        translated = translate_text(block.text, config)
        wrapped_text, font_size = fit_text_to_box(
            translated, block.font, block.font_size, block.bbox
        )
        page.add_redact_annot(block.bbox, fill=(1, 1, 1))
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
        page.insert_textbox(
            block.bbox,
            wrapped_text,
            fontname=block.font,
            fontsize=font_size,
            color=(0, 0, 0),
            align=fitz.TEXT_ALIGN_LEFT,
        )
    doc.save(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate a PDF into Estonian while preserving layout."
    )
    parser.add_argument("input", help="Input PDF path")
    parser.add_argument("output", help="Output PDF path")
    parser.add_argument(
        "--endpoint",
        default=os.getenv("TRANSLATE_ENDPOINT", "https://libretranslate.com/translate"),
        help="Translation API endpoint",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("TRANSLATE_API_KEY"),
        help="API key for translation service",
    )
    parser.add_argument(
        "--source",
        default=os.getenv("SOURCE_LANG"),
        help="Source language code (auto if omitted)",
    )
    parser.add_argument(
        "--target",
        default=os.getenv("TARGET_LANG", "et"),
        help="Target language code (default: et)",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=float(os.getenv("RATE_LIMIT_S", "0.0")),
        help="Delay between translation requests in seconds",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = TranslationConfig(
        endpoint=args.endpoint,
        api_key=args.api_key,
        source_lang=args.source,
        target_lang=args.target,
        rate_limit_s=args.rate_limit,
    )
    translate_pdf(args.input, args.output, config)


if __name__ == "__main__":
    main()
