from typing import List

from aiogram.enums import MessageEntityType
from aiogram.types import MessageEntity


def parse_html_to_md(html_text: str, entities: List[MessageEntity] | None):
    if not entities or not len(entities):
        return html_text

    type_priority = {
        MessageEntityType.BOLD: 0,
        MessageEntityType.ITALIC: 0,
        MessageEntityType.UNDERLINE: 0,
        MessageEntityType.STRIKETHROUGH: 0,
        MessageEntityType.BLOCKQUOTE: 0,
        MessageEntityType.PRE: 1,
        MessageEntityType.CODE: 2,
        MessageEntityType.TEXT_LINK: 3,
        MessageEntityType.CUSTOM_EMOJI: 4
    }

    sorted_entities = sorted(
        filter(lambda x: x.type in type_priority.keys(), entities),
        key=lambda x: type_priority.get(x.type, float('inf'))
    )

    html_text = parse_by_entity(html_text, sorted_entities)

    return html_text


def parse_by_entity(html_text: str, entities: List[MessageEntity]):
    for entity in entities:
        if entity.type == MessageEntityType.BOLD:
            html_text = replace_html_formatting_to_md(html_text, "<b>", "**")
            continue
        if entity.type == MessageEntityType.ITALIC:
            html_text = replace_html_formatting_to_md(html_text, "<i>", "*")
            continue
        if entity.type == MessageEntityType.BLOCKQUOTE:
            html_text = replace_html_formatting_to_md(html_text, "<blockquote>", "")
            continue
        if entity.type == MessageEntityType.UNDERLINE:
            html_text = replace_html_formatting_to_md(html_text, "<u>", "**")
            continue
        if entity.type == MessageEntityType.STRIKETHROUGH:
            html_text = replace_html_formatting_to_md(html_text, "<s>", "~~")
            continue
        if entity.type == MessageEntityType.CODE:
            html_text = replace_html_formatting_to_md(html_text, "<code>", "`")
            continue
        if entity.type == MessageEntityType.TEXT_LINK:
            html_text = replace_html_links_to_md(html_text)
            continue
        if entity.type == MessageEntityType.PRE:
            html_text = replace_html_code_block_to_md(html_text)
            continue
        if entity.type == MessageEntityType.CUSTOM_EMOJI:
            html_text = replace_tg_emoji_link_to_text(html_text)
            continue

    return html_text


def replace_html_formatting_to_md(html_text: str, html_chars: str, md_chars: str, start_index: int = 0):
    find_start_index = html_text.find(html_chars, start_index)
    find_end_index = html_text.find(html_chars.replace("<", "</"), start_index)
    if find_start_index == -1 or find_end_index == -1:
        return html_text
    len_html_chars = len(html_chars)
    html_text = (html_text[:find_start_index]
                 + md_chars + html_text[find_start_index + len_html_chars:find_end_index]
                 + md_chars + html_text[find_end_index + len_html_chars + 1:]
                 )
    if html_text.find(html_chars, find_end_index) != -1:
        html_text = replace_html_formatting_to_md(html_text, html_chars, md_chars,
                                                  find_end_index - (len_html_chars * 2 + 1) + (len(md_chars) * 2))
    return html_text


def replace_tg_emoji_link_to_text(html_text: str, start_index: int = 0):
    find_start_index = html_text.find("<tg-emoji emoji-id=\"", start_index)
    find_end_index = html_text.find("</tg-emoji>", start_index)
    if find_start_index == -1 or find_end_index == -1:
        return html_text
    cur_text_len = len(html_text)
    html_text = html_text[:find_start_index] + html_text[find_end_index - 1] + html_text[find_end_index + 11:]
    if html_text.find("<tg-emoji emoji-id=\"", find_end_index) != -1:
        html_text = replace_tg_emoji_link_to_text(html_text, find_end_index - (cur_text_len - len(html_text)))
    return replace_tg_emoji_link_to_text(html_text)


def replace_html_links_to_md(html_text: str, start_index: int = 0):
    """
    Replace html-links to markdown syntax in all html_text.\r\n
    Example:  \n
    From - <a href="https://google.com/">link</a> \n
    To - [link](https://google.com/)
    :param html_text: Текст html
    :param start_index:
    :return:
    """
    find_start_index = html_text.find("<a href=\"", start_index)
    find_end_index = html_text.find("</a>", start_index)
    if find_start_index == -1 or find_end_index == -1:
        return html_text

    full_link = html_text[find_start_index:find_end_index + 4]
    link_url = full_link.split("<a href=\"")[1].split("\">")[0]
    link_text = full_link.split("\">")[1].split("</a>")[0]
    if link_text == '\u200b\u200b' and link_url.startswith('https://telegra.ph/file/'):
        html_text = html_text.replace(full_link, f"![{link_url}]({link_url})\n")
    else:
        html_text = html_text.replace(full_link, f"[{link_text}]({link_url})")

    if html_text.find("<a href=\"", find_end_index) != -1:
        # -11 - it's a diff len of char between html link and markdown link without data
        # <a href=""></a> - 15
        # []() - 4
        html_text = replace_html_links_to_md(html_text, find_end_index - 11)
    return html_text


def replace_html_code_block_to_md(html_text: str, start_index: int = 0):
    find_start_index = html_text.find("<pre>", start_index)
    find_end_index = html_text.find("</pre>", start_index)
    if find_start_index == -1 or find_end_index == -1:
        return html_text

    code_string = html_text[find_start_index:find_end_index + 6]
    code_lang = ""

    if code_string.startswith("<pre><code class=\"language-"):
        code_lang = code_string.split("language-")[1].split("\">")[0]
        html_text = html_text.replace(code_string,
                                      f"""```{code_lang}\n{code_string.split('">')[1].split('</code>')[0]}\n```""")
    else:
        html_text = html_text.replace(code_string,
                                      f"```{code_lang}\n{code_string.split('<pre>')[1].split('</pre>')[0]}\n```")

    if html_text.find("<pre>", find_end_index) != -1:
        html_text = replace_html_code_block_to_md(html_text, find_end_index + 4)
    return html_text
