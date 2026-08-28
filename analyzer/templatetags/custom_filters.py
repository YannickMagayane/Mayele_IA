"""
Custom Django Template Filters for Formatting RAG AI Responses.

Provides clean markdown rendering by removing raw '###' headers, converting bold tags,
formatting bullet lists into elegant Tailwind HTML components, and ensuring professional display.

:Example:

>>> from analyzer.templatetags.custom_filters import clean_markdown
>>> html = clean_markdown("### Titre\\n* Point 1")
>>> print(html)
"""

import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="clean_markdown")
def clean_markdown(value: str) -> str:
    """
    Format raw markdown string into clean, professional HTML without raw '###' characters.

    :param value: Input raw text string from RAG engine or chat message.
    :type value: str
    :returns: Rendered HTML safe string with Tailwind styling.
    :rtype: str

    :Example:

    >>> clean_markdown("### Opportunités KCC\\n**Lieu** : Kolwezi")
    """
    if not value:
        return ""

    text = str(value).strip()

    # Step 1: Strip out raw ### or #### headers and convert them into styled section titles
    lines = text.split("\n")
    processed_lines = []
    in_list = False

    for line in lines:
        stripped_line = line.strip()

        # Check for headings starting with #, ##, ###, ####
        header_match = re.match(r"^#{1,6}\s*(.+)$", stripped_line)
        if header_match:
            if in_list:
                processed_lines.append("</ul>")
                in_list = False
            header_text = header_match.group(1).strip()
            # Remove any trailing hashes
            header_text = re.sub(r"\s*#+$", "", header_text)
            formatted_header = (
                f'<h3 class="text-xs md:text-sm font-extrabold text-indigo-950 uppercase tracking-wider mt-4 mb-2 pb-1 border-b border-indigo-100 flex items-center gap-2">'
                f'<span class="w-2 h-2 rounded-full bg-indigo-600 shrink-0"></span>'
                f'<span>{header_text}</span>'
                f'</h3>'
            )
            processed_lines.append(formatted_header)
            continue

        # Check for bullet list items: * or - or +
        bullet_match = re.match(r"^[\*\-\+]\s+(.+)$", stripped_line)
        if bullet_match:
            item_text = bullet_match.group(1).strip()
            if not in_list:
                processed_lines.append('<ul class="space-y-1.5 my-2 pl-1">')
                in_list = True
            formatted_item = (
                f'<li class="flex items-start gap-2 text-slate-700 text-xs md:text-sm font-medium leading-relaxed">'
                f'<span class="text-indigo-600 font-extrabold text-base leading-none select-none">•</span>'
                f'<span class="flex-1">{item_text}</span>'
                f'</li>'
            )
            processed_lines.append(formatted_item)
            continue

        # Check for numbered list items: 1., 2., etc.
        num_match = re.match(r"^(\d+)\.\s+(.+)$", stripped_line)
        if num_match:
            num = num_match.group(1)
            item_text = num_match.group(2).strip()
            if in_list:
                processed_lines.append("</ul>")
                in_list = False
            formatted_num_item = (
                f'<div class="flex items-start gap-2.5 my-1.5 p-2 bg-slate-50/80 border border-slate-100 rounded-xl">'
                f'<span class="w-5 h-5 rounded-lg bg-indigo-600 text-white font-extrabold text-[10px] flex items-center justify-center shrink-0 shadow-xs">{num}</span>'
                f'<div class="flex-1 text-slate-800 text-xs md:text-sm font-medium leading-relaxed">{item_text}</div>'
                f'</div>'
            )
            processed_lines.append(formatted_num_item)
            continue

        # Close list if active
        if in_list and not stripped_line:
            processed_lines.append("</ul>")
            in_list = False

        if stripped_line:
            processed_lines.append(f'<p class="text-xs md:text-sm leading-relaxed text-slate-700 font-medium my-2">{stripped_line}</p>')
        else:
            if not in_list:
                processed_lines.append('<div class="h-1"></div>')

    if in_list:
        processed_lines.append("</ul>")

    html_content = "\n".join(processed_lines)

    # Step 2: Convert bold markup **text** or __text__ to <strong>
    html_content = re.sub(r"\*\*(.*?)\*\*", r'<strong class="font-extrabold text-slate-900">\1</strong>', html_content)
    html_content = re.sub(r"__(.*?)__", r'<strong class="font-extrabold text-slate-900">\1</strong>', html_content)

    # Step 3: Convert italic markup *text* to <em>
    html_content = re.sub(r"(?<!\*)\*(?!\*)(.*?)\*", r'<em class="italic text-slate-800">\1</em>', html_content)

    # Step 4: Final safety pass to purge any lingering raw ### symbols
    html_content = re.sub(r"#{1,6}\s*", "", html_content)

    return mark_safe(html_content)
