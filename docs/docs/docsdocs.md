# Meta Documentation

> Meta documentation, i.e. documentation about the documentation.

The documentation is an [mkdocs][1] site, with the [material theme][2].
Documentation is written as markdown files, and gets rendered to html with
a nice theme by these tools.

[1]: https://www.mkdocs.org/
[2]: https://squidfunk.github.io/mkdocs-material/

## View

The documentation is hosted on Github Pages:

[https://divvun.github.io/CorpusTools/](https://divvun.github.io/CorpusTools)

If the documentation is built locally (see below), it is available in the **site/** folder.
Just open up the index.html page in a browser to view the documentation.

    firefox site/index.html

## Writing documentation

The actual _content_ of the documentation is in **docs/docs**, as markdown files.
The table of contents is in the `docs/properdocs.yml` file. When adding a new site,
it may be necessary to add the entry in the table of contents found in that file.

## Viewing the locally built documentation

### First time setup

From the repository root, create a virtual environment, activate it, and install
the project and documentation requirements:

    python3 -m venv .venv
    . .venv/bin/activate
    pip install -e .
    pip install -r docs/requirements.txt

When coming back to the documentation, only the second command (`. .venv/bin/activate`),
needs to be run.

### Running locally

From the `docs` directory, run the documentation while writing with

    properdocs serve

Then open up your browser to [http://localhost:8000](http://localhost:8000) to
see it.

To build the final documentation site locally, use

    properdocs build

It ends up as a static build in the **site/** directory.

### Updating the live page

The GitHub Actions documentation workflow builds and publishes the site when
documentation or source changes are pushed to the main branch.
