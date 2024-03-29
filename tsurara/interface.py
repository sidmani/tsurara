from simple_term_menu import TerminalMenu
from enum import Enum


class MainOptions(Enum):
    Known = "[k] known"
    Reveal = "[r] reveal meaning"
    Add = "[a] add"
    Skip = "[s] skip"
    Ignore = "[i] ignore"
    Quit = "[q] quit"


def show_tmenu(options, title, multi_select=False):
    menu = TerminalMenu(
        options, title=title, multi_select=multi_select, raise_error_on_interrupt=True
    )
    idx = menu.show()
    return options, idx


def show_main_options(base_str, revealed_str):
    options, idx = show_tmenu(
        [e.value for e in MainOptions],
        base_str,
    )

    option = MainOptions(options[idx])
    if option == MainOptions.Reveal:
        options, idx = show_tmenu(
            [e.value for e in MainOptions if e != MainOptions.Reveal],
            f"{base_str}\n{revealed_str}",
        )
        option = MainOptions(options[idx])

    return option


def select_word_forms(word: str, dic_data):
    quit = "[q] back to main menu"
    if len(dic_data.entries) == 1:
        entry = dic_data.entries[0]
    else:
        options, idx = show_tmenu(
            [e.text() for e in dic_data.entries] + [quit],
            f"Which entry for {word} ({dic_data.entries[0].kana_forms[0]})?",
        )
        if options[idx] == quit:
            return None
        entry = dic_data.entries[idx]

    if len(entry.kana_forms) == 1:
        kana = entry.kana_forms[0].text
    else:
        (options, idx) = show_tmenu(
            [e.text for e in entry.kana_forms] + [quit],
            f"Which kana form for {word} ({entry.kana_forms[0]})?",
        )
        if options[idx] == quit:
            return None
        kana = options[idx]

    if len(entry.kanji_forms) == 0:
        kanji = kana
    elif len(entry.kanji_forms) == 1:
        kanji = entry.kanji_forms[0].text
    else:
        (options, idx) = show_tmenu(
            [e.text for e in entry.kanji_forms] + [kana] + [quit],
            f"Which kanji form for {word} ({kana})?",
        )
        if options[idx] == quit:
            return None
        kanji = options[idx]

    glosses = [g.text for s in entry.senses for g in s.gloss]
    if len(glosses) == 1:
        sense = glosses[0]
    else:
        (options, idxs) = show_tmenu(
            glosses,
            f"Which definition for {kanji} ({kana})?",
            multi_select=True,
        )
        if len(options) == 0:
            raise Exception("You must select at least one definition!")

        sense = "; ".join([options[i] for i in idxs])

    return (kanji, kana, sense)
