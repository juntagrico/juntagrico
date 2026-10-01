from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
def highlight_search_term(text, search_term):
    """highlight search_term in text."""
    if not text or not search_term:
        return text

    text = escape(text)
    search_term = escape(search_term.strip())

    if not search_term:
        return text

    words = text.split()
    if not words:
        return text

    # Find all positions
    positions = []
    for i, word in enumerate(words):
        word_clean = re.sub(r'[^\w]', '', word).lower()
        if search_term.lower() in word_clean:
            positions.append(i)

    if not positions:
        return text

    # Create ranges and merge overlapping ones
    ranges = [(max(0, pos - 3), min(len(words), pos + 4)) for pos in positions]
    ranges.sort()

    merged_ranges = []
    for start, end in ranges:
        if merged_ranges and start <= merged_ranges[-1][1] + 1:
            # Merge overlapping ranges
            merged_ranges[-1] = (merged_ranges[-1][0], max(merged_ranges[-1][1], end))
        else:
            merged_ranges.append((start, end))

    # Build excerpts
    excerpts = []
    for start, end in merged_ranges:
        excerpt_words = words[start:end]
        prefix = '... ' if start > 0 else ''
        suffix = ' ...' if end < len(words) else ''

        excerpt_text = ' '.join(excerpt_words)
        highlighted = re.sub(
            rf'({re.escape(search_term)})',
            r'<mark>\1</mark>',
            excerpt_text,
            flags=re.IGNORECASE,
        )

        excerpts.append(f'{prefix}{highlighted}{suffix}')

    result = ' '.join(excerpts)
    return mark_safe(result)
