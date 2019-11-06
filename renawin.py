# !/usr/bin/python
# encoding: utf-8
#
# Renawin
# Application module
#
# Copyright (C) 2019 Yevhen Stohniienko <yeuhen.stohniyenko@ukr.net>
#
# This Source Code Form is subject to the terms of the Eclipse Public
# License v. 2.0. If a copy of the EPL was not distributed with this
# file, You can obtain one at https://www.eclipse.org/legal/epl-2.0/.

import os
import re
import argparse
import utils

# The function of renaming multiple files recursively
# Based on this article: https://www.coderslexicon.com/batch-
# renaming-of-files-using-recursion-in-python/
def renameFiles(path, callback, depth=1):
    """
    Runs callback for each file in directory and subdirectories.

    @param path: path to the start dir
    @param callback(file, path): callback to be called for each file
    or directory, where file is a file name and path is a path to file
    @param depth: depth of recursion (default: 1)
    """
    #print(u'renameFiles: path: ' + path)
    # Once we hit depth, just return (base case)
    if depth < 0: return
	
    # Make sure that a path was supplied and it is not a symbolic link
    if os.path.isdir(path) and not os.path.islink(path):
        #os.chdir(os.path.abspath(path))

        # Loop through each file in the start directory and create a
        # fullPath
        for file in os.listdir(path):
            fullPath = path + os.path.sep + file
            #fullPath = os.path.abspath(path) + os.path.sep + file
            #print(u'renameFiles: os.getcwd(): ' + os.getcwd())
            #fullPath = os.getcwd() + os.path.sep + file

            # Again, we don't want to follow symbolic links
            if not os.path.islink(fullPath):

                # If it is a directory, recursively call this function
                # giving that path and reducing the depth.
                if os.path.isdir(fullPath):
                    #print(u'dir: ' + fullPath)
                    # Recursively go to subdir
                    renameFiles(fullPath, callback, depth - 1)
                    # And then rename the directory itself
                    callback(file, path)
                else:
                    #print(u'fil: ' + fullPath)
                    # Rename the file
                    callback(file, path)
    return

# Function of renaming a file to make it Windows-friendly
# TODO: Add a name's length cutting up to the number of characters
# given in maxLen in full path starting from physical drive path
def renameForWin(fileName, ind=2, path=u'', baseDir=u'',
                 formatStr=u"{0}({1}){2}", replacement=u'-',
                 maxLen=0, isVerbose=1, isNono=1):
    """
    Renames file to make it Windows-friendly.

    @param fileName: the name of the file to be renamed
    @param ind: minimal index that can be added to a name when file
    with the same name is already exists (default: 2)
    @param path: path to the file to be renamed
    @param baseDir: base dir to log relative paths in verbose mode
    @param formatStr: reserved
    @param replacement: replacement string for symbols that file name
    cannot contain in Windows. Can be empty string (default: - (hyphen))
    @param maxLen: reserved
    @param isVerbose: true to print names of files successfully renamed
    @param isNono: true to print names of files to be renamed, but
    don't rename
    @return: (newFn, ind) where newFn is file name after renaming and
    ind is index that is incremented per unit in reference to the one 
    used in a file name
    """
    newFn = re.sub(r'\\|\/|:|\*|\?|"|<|>|\|', replacement, fileName)
    # Compare file names and check if it is unique in the
    # case-insensitive file system
    # When file name is already Windows-friendly, return immediately
    if (newFn == fileName and
        len(
            filter(
                lambda fn: (fn.upper() == fileName.upper()),
                os.listdir(path)
            )
        ) == 1 ):
            return (fileName, ind)
    # Function of adding an index to the end of file name
    def numFn(fn, ind, path):
        # Find the extension (if available) and rebuild file name
        # using the root of file name, index and the extension.
        root, ext = os.path.splitext(fn)
        numedFn = u"{0}({1}){2}".format(root, ind, ext)
        # If this name is already exists, increase the index
        if utils.path_exists_insensitive(path + os.path.sep + numedFn):
            return numFn(fn, ind+1, path)
        else:
            # If a name with index is unique, return it
            return (numedFn, ind+1)
    # If a new file name is already exists, add index to it
    if utils.path_exists_insensitive(path + os.path.sep + newFn):
        newFn, ind = numFn(newFn, ind, path)
    # Generate full paths with directory path and file name
    fullOld = path + os.path.sep + fileName
    fullNew = path + os.path.sep + newFn
    # Do rename and log it
    try:
        if not isNono:
            os.rename(fullOld, fullNew)
        if isVerbose:
            try:
                print(u"rename({0}, {1})".format(
                    os.path.relpath(fullOld, baseDir),
                    os.path.relpath(fullNew, baseDir)
                ))
            except (UnicodeDecodeError, UnicodeEncodeError):
                print(u"rename(<<Unicode filename>>)")
    except UnicodeDecodeError as e:
        # Skip invalid file name
        return (fileName, ind)
    # Return new file name and index for next occurrence of this name
    # Returned values are not used in this version
    return (newFn, ind)

# Validators based on this article: https://www.lixu.ca/2019/01/python-
# validator-action-for-argparse.html

# Validate Directory
class ValidateStartDir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Check if a Directory is empty or does not exist
        if os.path.exists(values) and os.path.isdir(values):
            if os.listdir(values):
                setattr(namespace, self.dest, values)
            else:    
                exitWithError("Given Directory is empty")
        else:
            exitWithError("Given Directory don't exists")

# Validate replacement
class ValidateReplacement(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if re.search(r'\\|\/|:|\*|\?|"|<|>|\|', values):
            exitWithError("A replacement parameter cannot contain "+
                "any of the following characters: "+
                "\ / : * ? \" < > | ")
        else:
            setattr(namespace, self.dest, values)

def exitWithError(msg):
    from sys import exit # this import is needed only in order to print
                         # an error message and exit
    exit("Error: {}".format(msg))

# Main function that covers all the others
def main():
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(prog="renawin",
        description="Rename multiple files recursively in order to "+
            "make it Windows-friendly.", add_help=False
    )
    parser.add_argument("path", metavar="PATH",
        type=unicode, action=ValidateStartDir, nargs='?',
        default=u".",
        help="A path to the start dir. Default is the current "+
            "working Directory."
    )
    parser.add_argument("-d", "--depth", dest="depth", metavar="N",
        type=int, default=float("inf"),
        help="Depth of recursion (default: infinite)."
    )
    parser.add_argument("-i", "--start-index", dest="startIndex",
        metavar="N", type=int, default=2,
        help="Start index for file name suffix (default: 2)."
    )
    parser.add_argument("-r", "--replacement", dest="replacement",
        metavar="S", type=unicode, action=ValidateReplacement,
        default=u'-',
        help="Replacement string for characters that a Windows file "+
            "name cannot contain. Can be empty (default: - (hyphen))."
    )
    parser.add_argument(
        "-v", "--verbose", dest="isVerbose",
        help="Verbose: print names of successfully renamed files.",
        action="store_true"
    )
    parser.add_argument(
        "-n", "--nono", dest="isNono",
        help="No action: print names of files to be renamed, but "+
            "don't rename.",
        action="store_true"
    )
    parser.add_argument("-V", "--version", action="version",
        version="%(prog)s 0.1.0",
        help="Show program's version number and exit."
    )
    parser.add_argument("-h", "--help", action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit."
    )
    args = parser.parse_args()
    print(args)
    #return

    # Destructure the arguments
    path = args.path
    depth = args.depth
    startIndex = args.startIndex
    replacement = args.replacement
    isVerbose = args.isVerbose or args.isNono
    isNono = args.isNono

    # Call function that does the rename
    renameFiles(os.path.abspath(path),
        # Renamer callback that is to be called for each file or
        # directory
        lambda file, path: (
            # Rename the file system object
            # TODO: Here the next index for each of the file name may be
            # cached and passed as a startIndex for optimizing in case
            # of a big number of the same names after the processing
            renameForWin(file, startIndex, path,
                baseDir=os.path.abspath(path),
                replacement=replacement,
                isVerbose=isVerbose, isNono=isNono
            )
        ), depth
    )

# Driver Code
if __name__ == '__main__':
    main()
