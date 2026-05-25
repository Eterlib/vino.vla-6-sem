"""Doit automation for MOOD project."""

import shutil
from pathlib import Path


DOIT_CONFIG = {"default_tasks": ["html"]}

POT_FILE = "mood/server/po/mood_server.pot"
PO_FILE = "mood/server/po/ru_RU/LC_MESSAGES/messages.po"
MO_FILE = "mood/server/po/ru_RU/LC_MESSAGES/messages.mo"
BABEL_CFG = "babel.cfg"
INDEX_HTML = "docs/build/html/index.html"
WHEEL_FILE = "dist/mood-0.1-py3-none-any.whl"
PYTHON = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"


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


def task_wheel():
    """Build wheel distribution."""
    PYTHON = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
    WHEEL_FILE = "dist/mood-0.1-py3-none-any.whl"
    return {
        "actions": [f"{PYTHON} -m build --wheel"],
        "task_dep": ["i18n"],
        "targets": [WHEEL_FILE],
        "clean": True,
    }


def task_test():
    """Run server+client integration tests."""
    return {
        "actions": ["pytest test_server.py -v"],
        "task_dep": ["i18n"],
        "file_dep": ["test_server.py"],
    }


def task_setup():
    """Install wheel into three clean pipenv environments."""
    import os
    import subprocess

    wheel = os.path.abspath("dist/mood-0.1-py3-none-any.whl")

    def install_envs():
        for env in ["/tmp/mood_srv", "/tmp/mood_cl1", "/tmp/mood_cl2"]:
            os.makedirs(env, exist_ok=True)
            subprocess.run(
                ["pipenv", "run", "pip", "install", wheel],
                cwd=env,
                check=True
            )
        print("Терминал 1: cd /tmp/mood_srv && pipenv run mood-server")
        print("Терминал 2: cd /tmp/mood_cl1 && pipenv run mood-client alice")
        print("Терминал 3: cd /tmp/mood_cl2 && pipenv run mood-client bob")

    return {
        "actions": [install_envs],
        "task_dep": ["wheel"],
    }
