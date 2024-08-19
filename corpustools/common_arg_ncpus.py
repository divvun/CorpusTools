import argparse
import multiprocessing
import os


# os.sched_getaffinity(0) is not available for MacOS, solution for it from
# https://stackoverflow.com/questions/74048135/alternatives-to-os-sched-getaffinity-for-macos
def _get_core_count() -> int:
    try:
        # NOTE: only available on some Unix platforms
        return len(os.sched_getaffinity(0))  # type: ignore[attr-defined]
    except AttributeError:
        return multiprocessing.cpu_count()


N_AVAILABLE_CPUS = _get_core_count()
CPU_CHOICES = {
    **{str(n): n for n in range(1, N_AVAILABLE_CPUS + 1)},
    **{
        "some": int(N_AVAILABLE_CPUS * 0.25),
        "half": int(N_AVAILABLE_CPUS * 0.5),
        "most": int(N_AVAILABLE_CPUS * 0.75),
        "all": N_AVAILABLE_CPUS,
    },
}


class NCpus(argparse.Action):
    """An argparse action for adding the common argument of "number of cpus"
    to use.

    Example usage:
        parser = argparse.ArgumentParser()
        parser.add_argument("--ncpus", action=NCpus)

        This will expose an optional argument --ncpus, which can have values
        of 1-<number of cpus on system>, as well as "some", "half", "most", and
        "all", which corresponds to 25%, 50%, 75% and 100% of the cpus,
        respectively. The parsed argument is always an int in range 1-<n cpus>.
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")

        some, half = CPU_CHOICES["some"], CPU_CHOICES["half"]
        most, all = CPU_CHOICES["most"], CPU_CHOICES["all"]
        self.CHOOSE_BETWEEN_STR = (
            f"Choose between 1-{N_AVAILABLE_CPUS}, "
            f"some ({some}), half ({half}), most ({most}) or all ({all})."
        )
        if "help" not in kwargs:
            kwargs["help"] = (
                "The number of cpus to use. If unspecified, defaults to using "
                f"as many cpus as it can. {self.CHOOSE_BETWEEN_STR}"
            )
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            value = CPU_CHOICES[values]
        except KeyError:
            parser.error(
                f"argument '{option_string}': invalid choice "
                f"'{values}'. {self.CHOOSE_BETWEEN_STR}"
            )
        setattr(namespace, self.dest, value)


# simple testing
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ncpus", action=NCpus)

    args = parser.parse_args()

    print(args)
