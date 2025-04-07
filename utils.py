from typing import List

from aiogram.enums import MessageEntityType
from emoji import EMOJI_DATA

from aiogram.types import MessageEntity


def count_emojis(char_array: List[str]) -> int:
    """
    Подсчитывает количество эмодзи в массиве символов.

    :param char_array: list of str - массив символов
    :return: int - количество эмодзи
    """
    emoji_count = 0

    # Проверяем каждый символ в строке
    for char in char_array:
        if char in EMOJI_DATA:
            emoji_count += 1

    return emoji_count


def is_emoji(char: str):
    # Упрощённая проверка (охватывает не все эмодзи!)
    emoji_ranges = [
        (0x1F600, 0x1F64F),  # Emoticons
        (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
        (0x1F680, 0x1F6FF),  # Transport & Map
        (0x2600, 0x26FF),  # Misc Symbols
        (0x2700, 0x27BF),  # Dingbats
    ]
    code = ord(char)
    return any(start <= code <= end for start, end in emoji_ranges)


def count_emojis_manual(char_array: List[str]):
    counter = 0
    for char in char_array:
        if len(char) == 1 and is_emoji(char):
            counter += 1
    return counter


def parse_text_to_md(text: str, entities: List[MessageEntity]) -> str:
    msg = list(text)
    index_append = 0
    for entity in entities:
        before_emoji_count = count_emojis(msg[:entity.offset])
        start_index = entity.offset - before_emoji_count
        end_index = start_index + entity.length
        if entity.type == MessageEntityType.BOLD:
            msg.insert(start_index + index_append, "**")
            index_append += 1
            msg.insert(end_index + index_append, "**")
            index_append += 1
            continue
        if entity.type == MessageEntityType.ITALIC:
            msg.insert(start_index + index_append, "*")
            index_append += 1
            msg.insert(end_index + index_append, "*")
            index_append += 1
            continue
        if entity.type == MessageEntityType.UNDERLINE:
            msg.insert(start_index + index_append, "**")
            index_append += 1
            msg.insert(end_index + index_append, "**")
            index_append += 1
            continue
        if entity.type == MessageEntityType.STRIKETHROUGH:
            msg.insert(start_index + index_append, "~~")
            index_append += 1
            msg.insert(end_index + index_append, "~~")
            index_append += 1
            continue
        if entity.type == MessageEntityType.CODE:
            msg.insert(start_index + index_append, "`")
            index_append += 1
            msg.insert(end_index + index_append, "`")
            index_append += 1
            continue
        if entity.type == MessageEntityType.PRE:
            start_string = "```"
            if entity.language:
                start_string += entity.language
            msg.insert(start_index + index_append, f"{start_string}\n")
            index_append += 1
            msg.insert(end_index + index_append, "\n```")
            index_append += 1
            continue
        if entity.type == MessageEntityType.TEXT_LINK:
            msg.insert(start_index + index_append, "[")
            index_append += 1
            msg.insert(end_index + index_append, f"]({entity.url})")
            index_append += 1
            continue
    return "".join(msg)


def parse_html_to_md(html_text: str, entities: List[MessageEntity]):
    if not len(entities):
        return html_text
    for entity in entities:
        if entity.type == MessageEntityType.BOLD:
            html_text = replace_html_formatting_to_md(html_text, "<b>", "**")
            continue
        if entity.type == MessageEntityType.ITALIC:
            html_text = replace_html_formatting_to_md(html_text, "<i>", "*")
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
        html_text = replace_html_formatting_to_md(html_text, html_chars, md_chars, find_end_index + len_html_chars + 1)
    return html_text


def replace_html_links_to_md(html_text: str, start_index: int = 0):
    """
    Преобразует html-ссылки в markdwon-ссылки во всем тексте.\r\n
    Пример:  \n
    ИЗ - <a href="https://google.com/">link</a> \n
    В - [link](https://google.com/)
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
    html_text = html_text.replace(full_link, f"[{link_text}]({link_url})")

    if html_text.find("<a href=\"", find_end_index) != -1:
        html_text = replace_html_links_to_md(html_text, find_end_index + 4)
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
        html_text = replace_html_code_block_to_md(html_text, find_end_index + 6)
    return html_text

