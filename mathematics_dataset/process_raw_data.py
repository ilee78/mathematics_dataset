""" Converts generated .txt data files into .tsv format.

Usage:
python process_raw_data.py
python process_raw_data.py --steps
"""

import csv
import os
import argparse
import math
import sys
import itertools

from absl import logging
import six
from six.moves import range
from arithmetic_parser import generate_datapoints

# # Number of training examples in each .txt file
# # This number must equal (per_train_module // 3) and (per_test_module)
# # Ex: NUM_EXAMPLES = 10,000 if per_train_module = 30,000 and per_test_module = 10,000
# NUM_EXAMPLES = 10000               # change as needed

# # Directory of raw data file (the --output_dir flag you specified when you ran generate_to_file.py)
# raw_data_dir = "raw_data"       # change as needed

# # Directory to output to
# output_filename = raw_data_dir + "_tsv"

# # Folder names
# folder_names = ["/extrapolate", "/interpolate", "/train-easy", "/train-medium", "/train-hard"]

# # File names
# file_header = "/arithmetic__"
# file_names = ["add_or_sub", "add_sub_multiple", "div", "mixed", "mul", "mul_div_multiple"]

# # Create output directory
# output_dir = os.path.expanduser(output_filename)
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)
#     # logging.fatal('output dir %s already exists', output_dir)
# logging.info('Writing to %s', output_dir)

# for folder in folder_names:
#     if not os.path.exists(output_filename + folder):
#         os.mkdir(output_filename + folder)      # create small_data_tsv/extrapolate
#     for file_ in file_names:
#         if folder == folder_names[0]:       # /extrapolate folder
#             if file_ == file_names[0] or file_ == file_names[2] or file_ == file_names[4]:
#                 txt_file = raw_data_dir + folder + file_header + file_ + "_big" + ".txt"
#             else:
#                 txt_file = raw_data_dir + folder + file_header + file_ + "_longer" + ".txt"
            
#             tsv_file = output_filename + folder + file_header + file_ + "_extrap" + ".tsv"
#             question_type = file_ + "_extrap"
        
#         else:     
#             txt_file = raw_data_dir + folder + file_header + file_ + ".txt"
#             tsv_file = output_filename + folder + file_header + file_ + ".tsv"
#             question_type = file_

#         f = open(txt_file, "r")

#         with open(tsv_file, "w") as out_file:
#             tsv_writer = csv.writer(out_file, delimiter='\t')
#             for i in range(NUM_EXAMPLES):
#                 question = f.readline().strip()
#                 answer = str(round(eval(f.readline().strip()), 12))
#                 if not args.num_steps:
#                     tsv_writer.writerow([question, answer, 1, question_type])
#                 else:
#                     datapoints = generate_datapoints(question, num_intermediates=args.num_steps)
#                     # Ensure validity of parsed datapoints
#                     assert(len(datapoints) > 0)
#                     if not math.isclose(eval(datapoints[0][1]), eval(answer)):
#                         print('parsed answer: {}\ngenerated answer: {}'.format(eval(datapoints[-1][1]), eval(answer)))
#                     assert(math.isclose(eval(datapoints[0][1]), eval(answer)))

#                     for q, a, finished in datapoints:
#                         tsv_writer.writerow([q, a, finished, question_type])


        
#         print(f'Writing to {tsv_file}')
#         f.close()

def sanitize_question(question):
    question = question.strip()
    question = ''.join(
        filter(lambda c: not c.isalpha(), question.split())
    )
    if question[-1] == '.' or question[-1] == '?':
        question = question[:-1]
    return question

def process_file(in_filename, out_filename, num_steps, question_type):
    with open(in_filename, "r") as in_file:
        with open(out_filename, "w") as out_file:
            tsv_writer = csv.writer(out_file, delimiter='\t')
            for i, (question, answer) in enumerate(itertools.zip_longest(*[in_file]*2)):
                if (i % 1000 == 0):
                    print('progress: {}'.format(i))
                question = sanitize_question(question)
                answer = answer.strip()
                # answer = str(round(eval(question, 12)))
                if not num_steps:
                    tsv_writer.writerow([question, answer, 1, question_type])
                else:
                    datapoints = generate_datapoints(question, num_intermediates=num_steps)
                    # Ensure validity of parsed datapoints
                    assert(len(datapoints) > 0)
                    # if not math.isclose(eval(datapoints[0][1]), eval(answer)):
                    #     print('parsed answer: {}\ngenerated answer: {}'.format(eval(datapoints[-1][1]), eval(answer)))
                    # assert(math.isclose(eval(datapoints[0][1]), eval(answer)))

                    for q, a, finished in datapoints:
                        tsv_writer.writerow([q, a, finished, question_type])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="single file to process", required=True)
    parser.add_argument("-o", "--output", type=str, help="output filename", required=True)
    parser.add_argument("--num-steps", type=int, help="number of intermediate steps to show", default=0)
    parser.add_argument("-t", "--type", type=str, help="question type in the file", default="N/A")

    args = parser.parse_args()
    process_file(args.file, args.output, args.num_steps, args.type)