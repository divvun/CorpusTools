import os
import operator


class SetupException(Exception):
    pass


class ExecutableMissingException(Exception):
    pass


def basename_noext(fname, ext):
    return os.path.basename(fname)[:-len(ext)]


def sort_by_value(table, **args):
    return sorted(table.iteritems(),
                  key=operator.itemgetter(1),
                  **args)


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
    if 'GTHOME' not in os.environ:
        raise SetupException("You have to set the environment variable GTHOME "
                             "to your checkout of langtech/trunk!")
    for program in program_list:
        if executable_in_path(program) is False:
            raise ExecutableMissingException(
                "Couldn't find %s in $PATH or it is not executable." % (
                    program.encode('utf-8'),))


def print_element(element, level, indent, out):
    '''Format an html document

    This function formats html documents for readability, to see
    the structure of the given document. It ruins white space in
    text parts.

    element is a lxml.etree element
    level is an integer indicating at what level this element is
    indent is an integer indicating how many spaces this element should
    be indented
    out is a file like buffer, e.g. an opened file
    '''
    tag = element.tag.replace('{http://www.w3.org/1999/xhtml}', 'html:')

    for i in range(0, level * indent):
        out.write(' ')
    out.write('<%s' % tag)

    for k, v in element.attrib.items():
        out.write(' %s="%s"' % (k.encode('utf8'), v.encode('utf8')))
    out.write('>\n')

    if element.text is not None and element.text.strip() != '':
        for i in range(0, (level + 1) * indent):
            out.write(' ')
        out.write('%s\n' % element.text.strip().encode('utf8'))

    for child in element:
        print_element(child, level + 1, indent, out)

    for i in range(0, level * indent):
        out.write(' ')
    out.write('</%s>\n' % tag)

    if level > 0 and element.tail is not None and element.tail.strip() != '':
        for i in range(0, (level - 1) * indent):
            out.write(' ')
        out.write('%s\n' % element.tail.strip().encode('utf8'))
