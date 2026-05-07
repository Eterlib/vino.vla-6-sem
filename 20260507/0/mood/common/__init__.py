"""Обычные утилиты для MOOD"""

import cowsay
from .constants import JGSBAT_BODY


def setup_cowsay():
    """Зарегистрируемые пользовательские символы cowsay"""
    cowsay.CHARS["jgsbat"] = JGSBAT_BODY
