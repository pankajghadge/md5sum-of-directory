#!/usr/bin/python -O

# Import the libraries we need for this script
import hashlib
import optparse
import os
import os.path
import sys


def read_hash_from_md5_file(md5_filename):
    """This function reads a hash out of a .md5 file."""

    with open(md5_filename) as file:
        for line in file:
            # this returns the hash if the MD5 file contained the hash only
            if len(line.rstrip()) == 32:
                return line.rstrip()
            # skip blank lines and semicolons
            if not line or line[0] == ';':
                continue
            # look for standard star divider character for .md5 files
            pos = line.find('*')
            if pos != -1:
                possible_hash = line[:pos].strip().lower()
                if len(possible_hash) == 32:
                    return possible_hash

    return None  # failed to find the hash


def generate_md5_hash(filename, block_size=2 ** 20, progress_blocks=128):
    """This function generates an md5 hash for a given file."""

    md5 = hashlib.md5()
    blocks = 0
    total_blocks = 1 + (os.path.getsize(filename) / block_size)
    with open(filename, 'rb') as file:
        while True:
            data = file.read(block_size)
            if not data:
                break
            md5.update(data)
            # Display progress in the command line
            if (blocks % progress_blocks) == 0:
                percentage_string = "{0}%".format(100 * blocks / total_blocks)
                sys.stdout.write("\r{1:<10}{0}".format(filename, percentage_string))
                sys.stdout.flush()
            blocks += 1
    return md5.hexdigest()


def generate_md5_file_for(filename, src_dir, dest_dir, md5_filename):

    dest_file_md5_full_path =  md5_filename.replace(src_dir, dest_dir)
    if not os.path.exists(os.path.dirname(dest_file_md5_full_path)):
        try:
            os.makedirs(os.path.dirname(dest_file_md5_full_path))
        except IOError:
            sys.stdout.write("ERROR: can't create directory {0}\n".format(dest_file_md5_full_path))


    """This function generates an md5 file for an existing file."""
    try:
        output_file = open(dest_file_md5_full_path, 'w')
    except IOError:
        sys.stdout.write("ERROR: can't write to file {0}\n".format(dest_file_md5_full_path))

    generated_hash = generate_md5_hash(filename)

    output_file.write("{0}\n".format(generated_hash))
    output_file.close()

    sys.stdout.write("\rDONE        {0}\n".format(filename))
    sys.stdout.flush()


def parse_args():
    """Read command line arguments and determine operation and directories """

    # Define the options taken by the script
    parser = optparse.OptionParser(
        usage="\n\t%prog source_dir destination_dir",
    )
    parser.add_option(
        "-v", "--verbose", action="store_true", dest="verbose",
        default=False, help="Print additional information for investigating missing files.",
    )

    # Parse options and read directory arguments from the command line
    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.print_help()
        sys.exit(1)

    src_dir = args[0]
    if not os.path.isdir(src_dir):
            print "ERROR: {0} is not a valid directory.".format(src_dir)
            sys.exit(1)


    # Check that the rest of the arguments are valid directories
    dest_dir = args[1]
    if not os.path.isdir(dest_dir):
            print "ERROR: {0} is not a valid directory.".format(dest_dir)
            sys.exit(1)

    return src_dir, dest_dir, options

""" Added by ganesh """
def generate_md5_dir_hash(top, filenames):

    md5         = hashlib.md5()
    filenames   = sorted(filenames)

    for each_file in filenames:
        full_file_name = os.path.join(top, each_file)
        if(os.stat(full_file_name).st_size != 0):
            with open(full_file_name, 'r') as md5file:
                data = md5file.read()
                md5.update(data)

    dir_md5_file_name = top + ".dir.md5"
    try:
        output_file = open(dir_md5_file_name, 'w')
    except IOError:
        sys.stdout.write("ERROR: can't write to file {0}\n".format(dir_md5_file_name))

    output_file.write("{0}\n".format(md5.hexdigest()))
    output_file.close()

""" Added by ganesh """
def generate_md5_for_dir(top, topdown=False):
    # Filter the directory entries in `top` into `dirnames` and `filenames`
    for (dirpath, dirnames, filenames) in os.walk(top,topdown):
       for each_dir in dirnames:
          filenames = []
          for each_file in os.listdir(os.path.join(dirpath,each_dir)):
                 full_file_name = os.path.join(dirpath,each_dir,each_file)
                 if os.path.isfile(full_file_name):
                     filenames.append(each_file)
          generate_md5_dir_hash(os.path.join(dirpath,each_dir), filenames)


def main():
    """Main procedure."""
    src_dir, dest_dir, options = parse_args()

    # Generate an .md5 file for files which don't have one
    #for filename, d in sorted(file_info_dicts.iteritems()):

    for (dirpath, dirnames, filenames) in os.walk(src_dir):
       for each_filename in filenames:
             full_file_path = os.path.join(dirpath, each_filename)
             generate_md5_file_for(full_file_path, src_dir, dest_dir, full_file_path + '.md5')

    print("=========================== generate_md5_for_dir ================================")

    generate_md5_for_dir(dest_dir);

    print("===============================================================================")


if __name__ == "__main__":
    main()
