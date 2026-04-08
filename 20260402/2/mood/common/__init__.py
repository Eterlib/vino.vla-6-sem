import cowsay
from .constants import JGSBAT_BODY


def setup_cowsay():
    """Register custom cowsay characters."""
    cowsay.CHARS["jgsbat"] = JGSBAT_BODY