Renawin
=======
The script allows to rename multiple files recursively in order to make it Windows-friendly by replacing characters that a Windows file name cannot contain with the specified ones.

As known, a Windows file name cannot contain any of the following characters: `\ / : * ? " < > |`. However, Linux allows to create files which contain mentioned symbols in their names, including those in the NTFS file system.

Also, some difficulties may appear with files having the same names in different letter cases. This script replaces invalid characters with the specified ones and adds index number in case of names’  coincidence.

## Requirements

* Linux or macOS
* Python 2 or 3

Tested only on Linux with Python 2.

## Installation

Just clone this repository into your appropriate directory and make symlink to renawin.py file in your local or global `bin` directory.

## Usage

```shell
  renawin [-d N] [-i N] [-r S] [-v] [-n] [-V] [-h] [PATH]
```

Arguments:

```shell
  PATH                  A path to the start dir. Default is the current
                        working Directory.
  -d N, --depth N       Depth of recursion (default: infinite).
  -i N, --start-index N
                        Start index for file name suffix (default: 2).
  -r S, --replacement S
                        Replacement string for characters that a Windows file
                        name cannot contain. Can be empty (default: -
                        (hyphen)).
  -v, --verbose         Verbose: print names of successfully renamed files.
  -n, --nono            No action: print names of files to be renamed, but
                        don't rename.
  -V, --version         Show program's version number and exit.
  -h, --help            Show the help message and exit.
```

## Examples

```shell
  renawin -n
```

Show files to be renamed in the current working Directory and its subdirectories with default settings.

```shell
  renawin -n --replacement "_"
```

Show files to be renamed in the current working Directory and its subdirectories with replacing characters that a Windows file name cannot contain with `_` (understroke) instead of default `-` (hyphen).

## Contributing

Any ideas, refactoring or remarks for improving the code would be welcome.

## Todo

* Add a name's length shortening up to the specified number of characters in full path on the physical drive
* Resolve issue with nono mode
* Add ability to detect and rename con, nul, prn, etc names
* Write the installation script

## Known issues

* In the nono mode the program adds index numbers to the same file names incorrectly due to the comparison with the files in the file system rather than with some special list.

## Release History

* 0.1.0 Initial release

## License

EPL-2.0 © Yevhen Stohniienko
