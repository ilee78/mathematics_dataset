# Converts generated .txt data files into .tsv format.

import csv
import os

from absl import logging
import six
from six.moves import range

# Number of training examples in each .txt file
# This number must equal (per_train_module // 3) and (per_test_module)
# Ex: NUM_EXAMPLES = 10,000 if per_train_module = 30,000 and per_test_module = 10,000
NUM_EXAMPLES = 10000               # change as needed

# Directory of raw data file (the --output_dir flag you specified when you ran generate_to_file.py)
raw_data_dir = "raw_data"       # change as needed

# Directory to output to
output_filename = raw_data_dir + "_tsv"

# Folder names
folder_names = ["/extrapolate", "/interpolate", "/train-easy", "/train-medium", "/train-hard"]

# File names
file_header = "/arithmetic__"
file_names = ["add_or_sub", "add_sub_multiple", "div", "mixed", "mul", "mul_div_multiple"]

# Create output directory
output_dir = os.path.expanduser(output_filename)
if os.path.exists(output_dir):
    logging.fatal('output dir %s already exists', output_dir)
logging.info('Writing to %s', output_dir)
os.makedirs(output_dir)

for folder in folder_names:
    os.mkdir(output_filename + folder)      # create small_data_tsv/extrapolate
    for file_ in file_names:
        if folder == folder_names[0]:       # /extrapolate folder
            if file_ == file_names[0] or file_ == file_names[2] or file_ == file_names[4]:
                txt_file = raw_data_dir + folder + file_header + file_ + "_big" + ".txt"
            else:
                txt_file = raw_data_dir + folder + file_header + file_ + "_longer" + ".txt"
            
            tsv_file = output_filename + folder + file_header + file_ + "_extrap" + ".tsv"
            question_type = file_ + "_extrap"
        
        else:     
            txt_file = raw_data_dir + folder + file_header + file_ + ".txt"
            tsv_file = output_filename + folder + file_header + file_ + ".tsv"
            question_type = file_

        f = open(txt_file, "r")

        with open(tsv_file, "w") as out_file:
            tsv_writer = csv.writer(out_file, delimiter='\t')
            for i in range(NUM_EXAMPLES):
                question = f.readline().strip()
                answer = f.readline().strip()
                tsv_writer.writerow([question, answer, question_type])
        
        print(f'Writing to {tsv_file}')
        f.close()