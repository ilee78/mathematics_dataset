import sys
import itertools
import argparse

from arithmetic_parser import generate_datapoints
from process_raw_data import sanitize_question

def print_histogram(hist: dict, max_width = 20):
    print('-' * 80)
    max_freq = max(hist.values())
    for k in sorted(hist.keys()):
        num_to_print = int(max_width * hist[k]/max_freq)
        print('{}:\t{}'.format(k, '*' * num_to_print))

def profile_question(question, counts):
    num_steps = len(generate_datapoints(question))
    if num_steps not in counts:
        counts[num_steps] = 0
    counts[num_steps] += 1

def profile_txt(filename):
    counts = {}
    with open(filename) as f:
        for i, (question, _) in enumerate(itertools.zip_longest(*[f]*2)):
            if i % 10000 == 0:
                print('{}...'.format(i))
            question = sanitize_question(question)
            profile_question(question, counts)
    return counts

def profile_tsv(filename):
    counts = {}
    with open(filename) as f:
        for i, sample in enumerate(f):
            if i % 10000 == 0:
                print('{}...'.format(i))
            question = sample.split('\t')[0]
            profile_question(question, counts)
    return counts


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--file', type=str, help='file to profile', required=True)
    argparser.add_argument('-t', '--type', type=str, help='what type of data file', choices=['txt', 'tsv'], required=True)
    args = argparser.parse_args()

    counts = profile_txt(args.file) if args.type == 'txt' else profile_tsv(args.file)
    print_histogram(counts)
    
            