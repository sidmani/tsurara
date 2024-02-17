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
