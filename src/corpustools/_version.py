"""Set the current CorpusTools version."""

from importlib.metadata import PackageNotFoundError, version


def get_version():
    try:
        return version("corpustools")
    except PackageNotFoundError:
        return "unknown"
