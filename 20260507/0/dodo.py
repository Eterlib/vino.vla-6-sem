"""Doit automation for MOOD project."""

import shutil
from pathlib import Path


DOIT_CONFIG = {"default_tasks": ["html"]}

POT_FILE = "mood/server/po/mood_server.pot"
PO_FILE = "mood/server/po/ru_RU/LC_MESSAGES/messages.po"
MO_FILE = "mood/server/po/ru_RU/LC_MESSAGES/messages.mo"
BABEL_CFG = "babel.cfg"
DOCS_BUILD = "docs/build/html"
INDEX_HTML = "docs/build/html/index.html"


def task_i18n_extract():
    """Extract messages from source files into .pot template."""
    return {
        "actions": [
            f"pybabel extract -F {BABEL_CFG} -o {POT_FILE} ."
        ],
        "file_dep": list(Path("mood/server").glob("**/*.py")) + [BABEL_CFG],
        "targets": [POT_FILE],
        "clean": True,
    }


def task_i18n_update():
    """Update or create .po file from .pot template."""
    return {
        "actions": [
            "pybabel update -i %(dependencies)s -d mood/server/po -l ru_RU "
            "|| pybabel init -i %(dependencies)s -d mood/server/po -l ru_RU"
        ],
        "file_dep": [POT_FILE],
        "targets": [PO_FILE],
    }


def task_i18n_compile():
    """Compile .po file into .mo binary."""
    return {
        "actions": [
            "pybabel compile -d mood/server/po"
        ],
        "file_dep": [PO_FILE],
        "targets": [MO_FILE],
        "clean": True,
    }


def task_i18n():
    """Run full i18n pipeline: extract, update, compile."""
    return {
        "actions": None,
        "task_dep": ["i18n_extract", "i18n_update", "i18n_compile"],
    }


def task_html():
    """Generate Sphinx HTML documentation."""
    src_files = (
        list(Path("docs/source").glob("**/*.rst")) +
        list(Path("mood").glob("**/*.py"))
    )
    return {
        "actions": ["sphinx-build -M html docs/source docs/build"],
        "file_dep": src_files,
        "targets": [INDEX_HTML],
        "clean": [(shutil.rmtree, ["docs/build", True])],
    }


def task_test():
    """Run server+client integration tests."""
    return {
        "actions": ["pytest test_server.py -v"],
        "task_dep": ["i18n"],
        "file_dep": ["test_server.py"],
    }


def task_sdist():
    """Build source distribution."""
    return {
        "actions": [
            "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 "
            "-m build --sdist"
        ],
        "task_dep": ["i18n"],
        "targets": ["dist/mood-0.1.tar.gz"],
        "clean": True,
    }


def task_wheel():
    """Build wheel distribution."""
    return {
        "actions": [
            "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 "
            "-m build --wheel"
        ],
        "task_dep": ["i18n"],
        "targets": ["dist/mood-0.1-py3-none-any.whl"],
        "clean": True,
    }
