import argparse

from corpustools import argparse_version
from corpustools.convertermanager import corpus_paths, sanity_check
from corpustools.corpuspath import CorpusPath
from corpustools.gold2correct import move_orig_to_correct, orig_to_text


def parse_options() -> argparse.Namespace:
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): the parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Turn 10% of files in a directory into .correct.txt files.",
    )

    parser.add_argument(
        "source",
        help="The directory where the original files exist",
    )

    args = parser.parse_args()

    return args


def categorise_files(source: str) -> dict[str, list[CorpusPath]]:
    """Categorise files based on their conversion status.

    Args:
        source: The path to the directory containing the files to categorise.

    Returns:
        A dictionary categorising files by their conversion status.
    """
    paths = corpus_paths([source])

    categorised: dict[str, list[CorpusPath]] = {}
    for file_path in paths:
        category = file_path.metadata.get_variable("conversion_status")
        if category is None:
            category = "uncategorised"
        categorised.setdefault(category, []).append(file_path)

    return categorised


def main() -> None:
    """Convert goldstandard files to .correct.txt files."""
    args = parse_options()

    sanity_check()
    categorised = categorise_files(args.source)
    total_files = sum(len(files) for files in categorised.values())
    already_correct = len(categorised.get("correct", [])) + len(
        categorised.get("goldstandard", [])
    )

    goal = (
        max(1, total_files // 10) - already_correct
    )  # Ensure at least one file is selected

    tenth = (categorised.get("standard", []) + categorised.get("uncategorised", []))[
        9::10
    ]

    for index, file_path in enumerate(tenth):
        if index >= goal:
            break
        print(f"Converting {file_path.orig} to .correct.txt")
        text = orig_to_text(file_path)
        move_orig_to_correct(file_path, text)

    print(f"Converted {min(goal, len(tenth))} files to .correct.txt")
