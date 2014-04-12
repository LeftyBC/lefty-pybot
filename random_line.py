import os
import random

def random_line_from_file(filename):
    line = ""
    while line == "":
        f = open(filename,'r')
        file_size = os.stat(filename)[6]

        f.seek((f.tell() + random.randint(0,file_size-1)) % file_size)
        # discard the first readline since it might read in the middle of the file
        f.readline()
        line = f.readline()
    return line.rstrip()
