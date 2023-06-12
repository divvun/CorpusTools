# Meta Documentation

> Meta documentation, i.e. documentation about the documentation.

The documentation is an [mkdocs][1] site, with the [material theme][2].
Documentation is written as markdown files, and gets rendered to html with
a nice theme by these tools.

[1]: https://www.mkdocs.org/
[2]: https://squidfunk.github.io/mkdocs-material/


## View

The documentation is hosted on Github Pages:

[https://giellalt.github.io/CorpusTools/](https://giellalt.github.io/CorpusTools)

If the documentation is built locally (see below), it is available in the __site/__ folder.
Just open up the index.html page in a browser to view the documentation.

    firefox site/index.html


## Writing documentation

The actual *content* of the documentation is in __docs/docs__, as markdown files.
The table of contents is in the `docs/mkdocs.yml` file. When adding a new site,
it may be necessary to add the entry in the table of contents found in that file.

## Viewing the locally built documentation

### First time setup

__mkdocs__ is a python tool. Create a virtual environment, activate it, and
install the requirements. The first and last step is only done once.

    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r -requirements.txt

When coming back to the documentation, only the second command (`. .venv/bin/activate`),
needs to be run.

### Running locally

To run the documentation while writing, use

    mkdocs serve

Then open up your browser to [http://localhost:8000](http://localhost:8000) to
see it.

To build the final documentation site locally, use

    mkdocs build

It ends up as a static build in the __site/__ directory.

### Updating the live page

To automatically build and publish the documentation on Github Pages, it's all done in a
single command:

    mkdocs gh-deploy

But please make sure to also commit the updates made to the markdown files themselves
in the main branch.
