import os
import lxml.etree as etree

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
    for i in range(0, level * indent):
        out.write(' ')
    out.write('<')
    out.write(element.tag.replace('{http://www.w3.org/1999/xhtml}', 'html:'))

    for k, v in element.attrib.items():
        out.write(' ')
        out.write(k.encode('utf8'))
        out.write('="')
        out.write(v.encode('utf8'))
        out.write('"')

    out.write('>\n')

    if element.text is not None and element.text.strip() != '':
        for i in range(0, (level + 1) * indent):
            out.write(' ')
        out.write(element.text.strip().encode('utf8'))
        out.write('\n')

    for child in element:
        print_element(child, level + 1, indent, out)

    for i in range(0, level * indent):
        out.write(' ')
    out.write('</')
    out.write(element.tag.replace('{http://www.w3.org/1999/xhtml}', 'html:'))
    out.write('>\n')

    if level > 0 and element.tail is not None and element.tail.strip() != '':
        for i in range(0, (level - 1) * indent):
            out.write(' ')
        out.write(element.tail.strip().encode('utf8'))
        out.write('\n')
