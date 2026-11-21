"""
IGRIS Phase 24 Tanglish Code-Switching Analysis Module
======================================================
Identifies Tamil script spans, English spans, Romanized Tamil candidates,
code-switch boundaries, Tamil suffix attachment, and discourse markers.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SpanInfo:
    start: int
    end: int
    script: str    # "TAMIL", "LATIN", "MIXED", "PUNCT"
    text: str


@dataclass
class CodeSwitchPoint:
    position: int
    from_script: str
    to_script: str
    left_context: str
    right_context: str


@dataclass
class TanglishAnalysis:
    total_chars: int
    tamil_char_count: int
    latin_char_count: int
    tamil_ratio: float
    latin_ratio: float
    spans: List[SpanInfo]
    code_switch_points: List[CodeSwitchPoint]
    discourse_markers_found: List[str]
    romanized_tamil_candidates: List[str]
    tamil_suffixes_detected: List[str]
    is_structurally_plausible: bool
    plausibility_notes: str


DISCOURSE_MARKERS = {
    "da", "pa", "di", "machan", "macha", "aiyo", "aiyoo", "seri",
    "romba", "kandippa", "thambi", "la", "dhan", "nu", "kooda",
    "apdiya", "illaya", "dhaan", "thaan",
}

ROMANIZED_TAMIL_PATTERNS = [
    r'\b[a-z]+nnu\b', r'\b[a-z]+chu\b', r'\b[a-z]+dhu\b',
    r'\b[a-z]+thu\b', r'\b[a-z]+nga\b', r'\b[a-z]+ngu\b',
    r'\b[a-z]+odu\b', r'\b[a-z]+oda\b', r'\b[a-z]+kku\b',
    r'\b[a-z]+ppu\b', r'\b[a-z]+ttu\b', r'\b[a-z]+aam\b',
]

TAMIL_SUFFIX_MARKERS = ["-ஐ", "-ல்", "-க்கு", "-இல்", "-ஆ", "-உடன்", "-ஆல்"]


def _is_tamil_cp(cp: int) -> bool:
    return 0x0B80 <= cp <= 0x0BFF


def _is_latin_cp(cp: int) -> bool:
    return (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A) or (0x00C0 <= cp <= 0x024F)


class TanglishAnalyzer:
    """Analyzes Tanglish text for code-switching patterns and structural properties."""

    def analyze(self, text: str) -> TanglishAnalysis:
        text_nfc = unicodedata.normalize('NFC', text)
        total = len(text_nfc)
        tamil_count = sum(1 for ch in text_nfc if _is_tamil_cp(ord(ch)))
        latin_count = sum(1 for ch in text_nfc if _is_latin_cp(ord(ch)))
        t_ratio = round(tamil_count / total, 4) if total > 0 else 0
        l_ratio = round(latin_count / total, 4) if total > 0 else 0

        spans = self._extract_spans(text_nfc)
        switch_points = self._find_code_switches(spans)
        words = re.findall(r'\b\w+\b', text_nfc.lower(), re.UNICODE)
        markers = [w for w in words if w in DISCOURSE_MARKERS]
        romanized = self._find_romanized_candidates(text_nfc)
        suffixes = [sfx for sfx in TAMIL_SUFFIX_MARKERS if sfx in text_nfc]

        plausible, notes = self._assess_plausibility(spans, switch_points, tamil_count, latin_count)

        return TanglishAnalysis(
            total_chars=total, tamil_char_count=tamil_count, latin_char_count=latin_count,
            tamil_ratio=t_ratio, latin_ratio=l_ratio, spans=spans,
            code_switch_points=switch_points, discourse_markers_found=markers,
            romanized_tamil_candidates=romanized, tamil_suffixes_detected=suffixes,
            is_structurally_plausible=plausible, plausibility_notes=notes,
        )

    def _extract_spans(self, text: str) -> List[SpanInfo]:
        spans = []
        if not text:
            return spans
        cur_script = self._char_class(text[0])
        start = 0
        for i in range(1, len(text)):
            sc = self._char_class(text[i])
            if sc != cur_script:
                spans.append(SpanInfo(start, i, cur_script, text[start:i]))
                cur_script = sc
                start = i
        spans.append(SpanInfo(start, len(text), cur_script, text[start:]))
        return spans

    def _char_class(self, ch: str) -> str:
        cp = ord(ch)
        if _is_tamil_cp(cp):
            return "TAMIL"
        if _is_latin_cp(cp):
            return "LATIN"
        return "PUNCT"

    def _find_code_switches(self, spans: List[SpanInfo]) -> List[CodeSwitchPoint]:
        switches = []
        script_spans = [s for s in spans if s.script in ("TAMIL", "LATIN")]
        for i in range(1, len(script_spans)):
            if script_spans[i].script != script_spans[i - 1].script:
                switches.append(CodeSwitchPoint(
                    position=script_spans[i].start,
                    from_script=script_spans[i - 1].script,
                    to_script=script_spans[i].script,
                    left_context=script_spans[i - 1].text[-15:],
                    right_context=script_spans[i].text[:15],
                ))
        return switches

    def _find_romanized_candidates(self, text: str) -> List[str]:
        candidates = []
        for pat in ROMANIZED_TAMIL_PATTERNS:
            candidates.extend(re.findall(pat, text.lower()))
        return list(set(candidates))

    def _assess_plausibility(self, spans, switches, tamil_c, latin_c) -> Tuple[bool, str]:
        if tamil_c == 0 and latin_c == 0:
            return False, "No script characters"
        if len(switches) > 20:
            return False, "Excessive code-switching (>20 points) suggests noise"
        if tamil_c > 0 and latin_c > 0:
            return True, "Bilingual content with plausible code-switch boundaries"
        if latin_c > 0 and tamil_c == 0:
            return True, "Latin-only text (may be Romanized Tamil or English)"
        return True, "Tamil-dominant text"
