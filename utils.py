from typing import List

from aiogram.enums import MessageEntityType

from aiogram.types import MessageEntity


def parse_html_to_md(html_text: str, entities: List[MessageEntity] | None):
    if not entities or not len(entities):
        return html_text


    # TODO: It's a bullshit, need correct sort and delete this
    format_entities = list(filter(
        lambda x: x.type in [MessageEntityType.BOLD, MessageEntityType.ITALIC, MessageEntityType.UNDERLINE,
                             MessageEntityType.STRIKETHROUGH], entities))
    code_entities = list(filter(lambda x: x.type == MessageEntityType.CODE, entities))
    pre_entities = list(filter(lambda x: x.type == MessageEntityType.PRE, entities))
    link_entities = list(filter(lambda x: x.type == MessageEntityType.TEXT_LINK, entities))

    html_text = parse_by_entity(html_text, [*format_entities, *pre_entities, *code_entities, *link_entities])

    return html_text

def parse_by_entity(html_text: str, entities: List[MessageEntity]):
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
        html_text = replace_html_formatting_to_md(html_text, html_chars, md_chars,
                                                  find_end_index - (len_html_chars * 2 + 1) + (len(md_chars) * 2))
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
        html_text = replace_html_code_block_to_md(html_text, find_end_index + 4)
    return html_text
