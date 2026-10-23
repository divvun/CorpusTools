# Corpus Tools

Tools to manipulate a giellalt corpus in different ways.

## Install and update from Apertium nightly

These tools are a part of
[Apertium nightly packages](https://wiki.apertium.org/wiki/Installation/Developers).

For Mac users, running the `install-nightly.sh` suffices, Linux users will have
to run `<package-manager> install <name of package>`, as well (search for corpustools in
the package system).

To update the tools on Mac, run `install-nightly.sh`. On Linux, update packages
using the package manager.

## Install and update using pipx

- [Install pipx](https://pypa.github.io/pipx/installation/)
- Run `pipx install --force git+https://github.com/divvun/CorpusTools.git`

## Development

- [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- Run `uv sync` to install the project and development dependencies.
- Run `uv run pytest` to run the test suite.

[API and manual pages](https://divvun.github.io/CorpusTools/)
