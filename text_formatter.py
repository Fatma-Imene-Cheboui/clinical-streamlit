"""
Text formatting functions for clinical notes
"""
import re
from typing import List
from config import CARD_WIDTH_CHARS


def format_clinical_text(text: str) -> str:
    """Format clinical text with colored section headers"""
    sections = {
        r"(?im)^\s*(FDRCV\s+ET\s+)?ATCDS?\b\s*:?\s*": (
            "<div class='section-header atcd'><span class='emoji'>🟦</span> ATCD</div><br>",
            "#5D9CEC"
        ),
        r"(?im)^\s*(HDM|HISTOIRE\s+DE\s+LA\s+MALADIE)\b\s*:?\s*": (
            "<div class='section-header hdm'><span class='emoji'>🟪</span> HDM</div><br>",
            "#AC92EC"
        ),
        r"(?im)^\s*EXAMEN\s+CLINIQUE\b\s*:?\s*": (
            "<div class='section-header exam'><span class='emoji'>🟩</span> Examen clinique</div><br>",
            "#4FC1E9"
        ),
        r"(?im)^\s*ECG\b\s*:?\s*": (
            "<div class='section-header ecg'><span class='emoji'>🟥</span> ECG</div><br>",
            "#ED5565"
        ),
        r"(?im)^\s*ETT\b(\s+DES\s+URGENCES)?\b\s*:?\s*": (
            "<div class='section-header ett'><span class='emoji'>🟧</span> ETT</div><br>",
            "#FC6E51"
        ),
        r"(?im)^\s*CORONAROGRAPHIE\b\s*:?\s*": (
            "<div class='section-header coro'><span class='emoji'>🫀</span> Coronarographie</div><br>",
            "#E9573F"
        ),
        r"(?im)^\s*CONDUITE\s+TENUE\s+EN\s+SALLE\s+D['']URGENCE\b\s*:?\s*": (
            "<div class='section-header conduite'><span class='emoji'>🟨</span> Conduite tenue en salle d'urgence</div><br>",
            "#FFCE54"
        ),
        r"(?im)^\s*CAT\b\s*:?\s*": (
            "<div class='section-header cat'><span class='emoji'>🟫</span> CAT</div><br>",
            "#A0826D"
        ),
    }

    for pattern, (title, color) in sections.items():
        text = re.sub(pattern, title, text)

    text = text.replace("\n", "<br>")
    return text


def clean_content(text: str) -> str:
    """Remove excessive empty lines"""
    lines = text.split("<br>")
    cleaned = []
    prev_empty = False
    
    for line in lines:
        is_empty = not line.strip()
        if is_empty:
            if not prev_empty:
                cleaned.append(line)
            prev_empty = True
        else:
            cleaned.append(line)
            prev_empty = False
    
    return "<br>".join(cleaned)


def calculate_line_height(line: str, card_width_chars: int = CARD_WIDTH_CHARS) -> float:
    """Calculate visual height for a line based on wrapping"""
    if not line.strip():
        return 0
    elif '<div class="section-header' in line:
        return 60
    else:
        char_count = len(line.strip())
        wrapped_lines = max(1, (char_count + card_width_chars - 1) // card_width_chars)
        return 24 * wrapped_lines


def split_content_dynamically(text: str, max_height: int = 500) -> List[str]:
    """Distribute content equally across minimum cards needed"""
    text = clean_content(text)
    lines = [l for l in text.split("<br>") if l.strip()]
    
    if not lines:
        return [text]
    
    PADDING = 32
    line_heights = [calculate_line_height(line) for line in lines]
    total_height = sum(line_heights) + PADDING
    num_cards = max(1, -(-total_height // max_height))
    target_height_per_card = total_height / num_cards
    
    sections = []
    current_section = []
    current_height = PADDING
    
    for i, (line, line_height) in enumerate(zip(lines, line_heights)):
        remaining_cards = num_cards - len(sections)
        should_break = False
        
        if remaining_cards > 1:
            if current_height + line_height > target_height_per_card * 1.15:
                if current_height > PADDING + 40:
                    should_break = True
            if current_height + line_height > max_height:
                should_break = True
        
        if should_break and current_section:
            sections.append("<br>".join(current_section))
            current_section = [line]
            current_height = PADDING + line_height
        else:
            current_section.append(line)
            current_height += line_height
    
    if current_section:
        sections.append("<br>".join(current_section))
    
    if len(sections) >= 2:
        section_heights = []
        for section in sections:
            section_lines = section.split("<br>")
            height = sum(calculate_line_height(l) for l in section_lines) + PADDING
            section_heights.append(height)
        
        avg_height = sum(section_heights) / len(section_heights)
        variance = sum((h - avg_height) ** 2 for h in section_heights) / len(section_heights)
        
        if variance > (avg_height * 0.2) ** 2:
            all_lines = []
            for section in sections:
                all_lines.extend(section.split("<br>"))
            
            sections = []
            lines_per_card = len(all_lines) / num_cards
            current_section = []
            target_lines = lines_per_card
            
            for idx, line in enumerate(all_lines):
                current_section.append(line)
                if len(current_section) >= target_lines and len(sections) < num_cards - 1:
                    sections.append("<br>".join(current_section))
                    current_section = []
                    target_lines = lines_per_card * (len(sections) + 1) - sum(
                        len(s.split("<br>")) for s in sections
                    )
            
            if current_section:
                sections.append("<br>".join(current_section))
    
    return sections if sections else [text]