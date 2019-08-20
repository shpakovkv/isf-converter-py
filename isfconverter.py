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
    print("File list:{}".format(file_list))  # debug
    file_list.sort()
    return file_list


def check_file_list(file_list):
    """User input file list check.
    Replaces file names with full paths.

    :param file_list:  a list with ISF files names

    :return:  None
    """
    print("file list = {}".format(file_list))       # debug
    for idx, name in enumerate(file_list):
        print("name = {}".format(name))             # debug
        assert os.path.isfile(name), "Cannot find file {} ".format(name)
        file_list[idx] = os.path.abspath(name)


def check_args(options):
    """Input options global check.

    Returns changed options with converted values.

    options -- namespace with options
    """
    # input directory and files check
    if options.src_dir:
        options.src_dir = options.src_dir.strip()
        print("New out dir: {}".format(options.src_dir))            # debug
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
        if options.out_dir:
            for idx, name in enumerate(options.output_file_names):
                options.output_file_names[idx] = os.path.join(out_path, name)
        else:
            for idx, name in enumerate(options.output_file_names):
                options.output_file_names[idx] = os.path.abspath(name)


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
    print("Output file: {}".format(filename))               # debug
    with open(filename, 'w') as fid:
        lines = []
        if save_head:
            lines.append(head)
        # add data
        for row in range(len(x)):
            s = delimiter.join([value_format % x[row], value_format % y[row]]) + "\n"
            lines.append(s)
        fid.writelines(lines)


def main():
    parser = get_parser()
    args = parser.parse_args()
    check_args(args)
    print(args)                                                     # debug
    print("==================================================")     # debug
    for filename in args.files:
        new_filename = filename[:]
        if filename.upper().endswith(".ISF"):
            new_filename = new_filename[:-4] + ".csv"
        print("Processing file: {}".format(filename))                               # debug
        save_csv(new_filename, *isfreader.read_isf(filename), save_head=args.head)
        print()                                                                     # debug


if __name__ == "__main__":
    # filename = "F:\\PROJECTS\\Python\\Converter_ISF\\isfread-py\\testfiles\\tek0000CH3.isf"
    # # x, y, head = isfreader.read_isf(filename)
    # numpy_save_csv(filename, *isfreader.read_isf(filename))
    main()
