import sys
import itertools

from arithmetic_parser import generate_datapoints
from process_raw_data import sanitize_question

def print_histogram(hist: dict, max_width = 20):
    max_freq = max(hist.values())
    for k in sorted(hist.keys()):
        num_to_print = int(max_width * hist[k]/max_freq)
        print('{}:\t{}'.format(k, '*' * num_to_print))


if __name__ == '__main__':
    assert len(sys.argv) > 1, 'must provide filename to profile'
    filename = sys.argv[1]
    
    counts = {}
    with open(filename) as f:
        for (question, _) in itertools.zip_longest(*[f]*2):
            question = sanitize_question(question)
            num_steps = len(generate_datapoints(question))
            if num_steps not in counts:
                counts[num_steps] = 0
            counts[num_steps] += 1

    print_histogram(counts)
    
            