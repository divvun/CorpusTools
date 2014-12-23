import os

class SetupException(Exception):
    pass

class ExecutableMissingException(Exception):
    pass

def is_executable(fullpath):
    return os.path.isfile(fullpath) and os.access(fullpath, os.X_OK)

def path_possibilities(program):
    return (os.path.join(path.strip('"'),
                         program)
            for path
            in os.environ["PATH"].split(os.pathsep))

def executable_in_path(program):
    fpath, fname = os.path.split(program)
    if fpath:
        return is_executable(program)
    else:
        return any(is_executable(possible_path)
                   for possible_path in
                   path_possibilities(program))

def sanity_check(program_list):
    u"""Look for programs and files that are needed to do the analysis.
    If they don't exist, raise an exception.
    """
    if not 'GTHOME' in os.environ:
        raise SetupException("You have to set the environment variable GTHOME to "
                             "your checkout of langtech/trunk!")
    for program in program_list:
        if executable_in_path(program) is False:
            raise ExecutableMissingException(
                "Couldn't find %s in $PATH or it is not executable." % (
                    program.encode('utf-8'),))
