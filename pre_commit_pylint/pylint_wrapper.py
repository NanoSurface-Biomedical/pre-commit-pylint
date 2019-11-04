#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""A wrapper for pylint that implements score limit and Python 3 porting check.
Forked from Botpy/pre-commit-pylint
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import re
import sys

import six
from pylint import epylint as lint


# Code copy from:
# https://github.com/sebdah/git-pylint-commit-hook/blob/master/git_pylint_commit_hook/commit_hook.py#L84-L98
_SCORE_REGEXP = re.compile(
    r'^\s+Your\ code\ has\ been\ rated\ at\ (\-?[0-9\.]+)/10')


def _parse_score(output):
    """Parse the score out of pylint's output as a float
    If the score is not found, return 0.0.
    """
    # If output is empty that means the file is empty.
    if output.strip() == "":
        return 10.0

    for line in output.splitlines():
        if isinstance(line, six.binary_type):
            line = line.decode("utf-8")

        match = re.match(_SCORE_REGEXP, line)
        if match:
            return float(match.group(1))
    return 0.0
_ERROR_CODE_REGEXP=re.compile(r'^.+:\d+: \w+ \((\w\d\d\d\d),')
lines_to_print=[]
def _is_not_acceptable_pylint_error(output,list_of_codes):
    global lines_to_print
    is_acceptable=True
    for line in output.splitlines():
        lines_to_print.append(line)
        if line[:5]=='*****':
            continue
        match = re.match(_ERROR_CODE_REGEXP,line)
        if match:
            if match.group(1) not in list_of_codes:
                is_acceptable=False
    return is_acceptable

def _run_pylint(argv=None):
    return lint.py_run(" ".join(argv), return_std=True)


def check_score(argv=None):
    """Check score limit."""

    # if argv is None:
    #     argv = sys.argv[1:]

    # parser = argparse.ArgumentParser(__name__)
    # parser.add_argument('filenames', nargs='*', help='filenames to check.')

    # parser.add_argument("--limit", default=8.0, type=float,
    #                     help=('Score limit, files with a lower score will '
    #                           'stop the commit. Default: 8.0'))

    # ns, argv = parser.parse_known_args(argv)

    # all_passed = True

    # for i, filename in enumerate(ns.filenames):
    #     print("Running pylint on %s (file %d/%d).." % (
    #         filename, i + 1, len(ns.filenames)), end="\t")

    #     pylint_stdout, pylint_stderr = _run_pylint([filename] + argv)

    #     output = pylint_stdout.getvalue()
    #     score = _parse_score(output)
    #     passed = score >= ns.limit
    #     print("%.2f/%.2f" % (score, ns.limit), end="\t")

    #     if (not passed):
    #         print("FAILED")
    #         print(output)
    #         all_passed = False
    #     else:
    #         print("PASSED")
    if argv is None:
        argv = sys.argv[1:]
    
    parser = argparse.ArgumentParser(__name__)
    parser.add_argument('--codes-to-allow', help='csv of codes to allow passing while still displaying them.')
    

    ns, argv = parser.parse_known_args(argv)
    list_of_codes = ns.codes_to_allow.split(',')
    if len(list_of_codes) > 0:
        print ("Displaying any instances of these codes but still allowing commit: %s" % ' '.join(list_of_codes))
    all_passed = True
    
    new_argv=[]
    # remove the file list generated by pre-commit from the 
    for this_arg in argv:
        if len(this_arg) > 3:
            if this_arg[-3:]=='.py':
                continue
        new_argv.append(this_arg)
    

    pylint_stdout, pylint_stderr = _run_pylint(new_argv)

    output = pylint_stdout.getvalue()
    
    all_passed = _is_not_acceptable_pylint_error(output,list_of_codes)
    score = _parse_score(output)
    if score < 10:
        for this_line in lines_to_print:
            print (this_line)
    # passed = score >= ns.limit
    # print("%.2f/%.2f" % (score, ns.limit), end="\t")

    # if (not passed):
    #     print("FAILED")
    #     print(output)
    #     all_passed = False
    # else:
    #     print("PASSED")

    sys.exit(all_passed - 1)


def check_py3k():
    """Check Python3 porting."""
    argv = sys.argv[1:]
    check_score(argv + ["--py3k", "--limit=10"])
