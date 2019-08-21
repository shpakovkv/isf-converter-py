#!/usr/bin/env python
# coding: utf-8

"""This script adds command line interface (CLI) to the isfreader.py script.

Now you may specify a directory with .isf binary files and the script wil convert all the files
to csv format and save to a specified output directory.

Simple usage:
python isfconverter.py -f inputfile.isf -s outputfile.csv
python isfconverter.py -d input-dir-path -o output-dir-path


Author: Konstantin Shpakov, august 2019.
"""

from __future__ import print_function
import os
import sys
import isfreader
import argparse

VERBOSE = False

def get_parser():
    """Returns final parser.
    """
    dics_words = ""

    epilog_words = ""

    manual_words = ("python %(prog)s -f filename\n"
                    "       python %(prog)s -d path/to/dir\n"
                    "       python %(prog)s -d path/to/dir -o path/to/save\n"
                    "       python %(prog)s @file_with_options")

    parser = argparse.ArgumentParser(
        parents=[get_file_params_parser()],
        prog='ISFConverter.py',
        description=dics_words, epilog=epilog_words, usage=manual_words,
        fromfile_prefix_chars='@',
        formatter_class=argparse.RawTextHelpFormatter)
    return parser


def get_file_params_parser():
    """Returns the parser of parameters of input files.
    """
    file_params_parser = argparse.ArgumentParser(add_help=False)
    group = file_params_parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '-d', '--directory',
        action='store',
        metavar='DIR',
        dest='src_dir',
        default='',
        help='specify the directory containing data files.\n'
             'Default= the folder containing this code.\n\n')

    group.add_argument(
        '-f', '--files',
        action='store',
        nargs='+',
        metavar='FILE',
        dest='files',
        help='specify one or more (space separated) input file names \n'
             'after the flag.\n\n')

    file_params_parser.add_argument(
        '--head', '--include-header',
        action='store_true',
        dest='head',
        help='adds header lines to the output files.'
    )

    file_params_parser.add_argument(
        '-o', '--output-dir',
        action='store',
        metavar='DIR',
        dest='out_dir',
        default='',
        help='specify the output directory.\n\n')

    file_params_parser.add_argument(
        '-s', '--save_as',
        action='store',
        nargs='+',
        metavar='FILE',
        dest='output_file_names',
        default=[],
        help='specify one or more (space separated) output file names \n'
             'after the flag. The number of the output file names \n'
             'must be equal to the number of the input file names.\n\n')

    file_params_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='verbose',
        help='shows more information during the process.\n\n')

    return file_params_parser


def get_file_list(dir, ext='ISF'):
    """Return the list of ISF files from the directory 'dir'.

    dir -- the directory containing the target files
    ext -- the list of extensions of files

        :param dir:         the directory containing target files
        :param ext:         target file extension

        :type dir:          string
        :type ext:          string

        :return:            the list of files to be converted
        :rtype:             list of strings
        """
    assert dir, ("Specify the directory (-d) containing the "
                 "'{}' files. See help for more details.".format(ext))
    path = os.path.abspath(dir)
    file_list = [os.path.join(path, x) for x in os.listdir(path)
                 if os.path.isfile(os.path.join(path, x))
                 and (x.upper().endswith(ext.upper()))]
    file_list.sort()
    return file_list


def check_file_list(file_list):
    """User input file list check.
    Replaces file names with full paths.

    :param file_list:  a list with ISF files names

    :return:  None
    """
    for idx, name in enumerate(file_list):
        assert os.path.isfile(name), "Cannot find file {} ".format(name)
        file_list[idx] = os.path.abspath(name)


def check_args(options):
    """Input options global check.

    Returns changed options with converted values.

    options -- namespace with options
    """
    global VERBOSE
    if options.verbose:
        VERBOSE = True

    # input directory and files check
    if options.src_dir:
        options.src_dir = options.src_dir.strip()
        assert os.path.isdir(options.src_dir), \
            "Can not find directory {}".format(options.src_dir)
        options.files = get_file_list(options.src_dir)
    else:
        options.src_dir = sys.path
    if options.files:
        check_file_list(options.files)
    if options.out_dir:
        if not os.path.isdir(options.out_dir):
            os.makedirs(options.out_dir)
        out_path = options.out_dir
    else:
        out_path = options.src_dir
    if options.output_file_names:
        n_in = len(options.files)
        n_out = len(options.output_file_names)
        assert n_in == n_out, ("The number of the output file names ({})"
                               " must be equal to the number of the input"
                               " file names ({}).".format(n_in, n_out))
    else:
        for idx, name in enumerate(options.files):
            new_name = name[:]
            if new_name.upper().endswith(".ISF"):
                new_name = new_name[:-4] + ".csv"
            if options.out_dir:
                new_name = os.path.basename(new_name)
                options.output_file_names.append(os.path.join(out_path, new_name))
            else:
                options.output_file_names.append(os.path.abspath(new_name))


def save_csv(filename, x, y, head, save_head=False, delimiter=",", precision=18):
    """Saves data to a CSV file.

    :param x:          x_data array
    :param y:          y_data array
    :param head:       headerlines
    :param filename:   full path
    :param save_head:  write header lines or not
    :param delimiter:  the CSV file delimiter (default is ",")
    :param precision:  the number of significant digits (total before and after the decimal point)

    :return:           None
    """
    assert isinstance(precision, int), "Precision must be integer"
    if precision > 18:
        precision = 18
    value_format = '%0.' + str(precision) + 'e'

    # check filename
    if len(filename) < 4 or filename[-4:].upper() != ".CSV":
        filename += ".csv"
    folder_path = os.path.dirname(filename)
    if folder_path and not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    if VERBOSE:
        print("Output file: {}".format(filename))
    with open(filename, 'w') as fid:
        lines = []
        if save_head:
            str_head = "; ".join(": ".join((str(val) for val in line)) for line in head.items())
            lines.append(str_head)
        # add data
        for row in range(len(x)):
            s = delimiter.join([value_format % x[row], value_format % y[row]]) + "\n"
            lines.append(s)

        fid.writelines(lines)
    if VERBOSE:
        print("Saved.")


def main():
    parser = get_parser()
    args = parser.parse_args()
    check_args(args)
    for idx, filename in enumerate(args.files):
        if VERBOSE:
            print("Processing file: {}".format(filename))
        save_csv(args.output_file_names[idx], *isfreader.read_isf(filename), save_head=args.head)
        if VERBOSE:
            print()


if __name__ == "__main__":
    main()
