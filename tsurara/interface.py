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
            f"{base_str} {revealed_str}",
        )
        option = MainOptions(options[idx])

    return option


def select_word_forms(word, dic_data):
    if len(dic_data.entries) == 1:
        entry = dic_data.entries[0]
    else:
        _, entry_idx = show_tmenu(
            [e.text() for e in dic_data.entries],
            f"Which entry for {word.feature.lemma} ({dic_data.entries[0].kana_forms[0]})?",
        )
        entry = dic_data.entries[entry_idx]

    if len(entry.kana_forms) == 1:
        kana = entry.kana_forms[0].text
    else:
        (options, idx) = show_tmenu(
            [e.text for e in entry.kana_forms],
            f"Which kana form for {word.feature.lemma} ({entry.kana_forms[0]})?",
        )
        kana = options[idx]

    if len(entry.kanji_forms) == 0:
        kanji = kana
    elif len(entry.kanji_forms) == 1:
        kanji = entry.kanji_forms[0].text
    else:
        (options, idx) = show_tmenu(
            [e.text for e in entry.kanji_forms] + [kana],
            f"Which kanji form for {word.feature.lemma} ({kana})?",
        )
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
