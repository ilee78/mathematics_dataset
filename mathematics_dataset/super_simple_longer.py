import random
import os
import csv

def make_q_a(num_digits, num_ops):
    ops = ["+" if random.random() >= 0.5 else "-" for i in range(num_ops)]
    a = random.randint(10 ** (num_digits[0] - 1), (10 ** num_digits[0]) - 1)
    q = str(a)

    for i in range(len(ops)):
        q += ops[i]
        num = random.randint(10 ** (num_digits[i + 1] - 1), (10 ** num_digits[i + 1]) - 1)
        if ops[i] == "+":
            a += num
        else:
            a -= num
        q += str(num)
    return q, a

if not os.path.exists("raw_data_tsv"):
    os.makedirs("raw_data_tsv")

with open("raw_data_tsv/super_simple_longer.tsv", "w") as fout:
    tsv_writer = csv.writer(fout, delimiter='\t')
    n = 100000
    # q_len = 0
    
    for i in range(n):
        num_ops = random.randint(1, 3)
        if num_ops == 1:
            max_digits = 30
        if num_ops == 2:
            max_digits = 20
        if num_ops == 3:
            max_digits = 15

        num_digits = [random.randint(max_digits // 2, max_digits) for i in range(num_ops + 1)]
        q, a = make_q_a(num_digits, num_ops)
        tsv_writer.writerow([q, a, 1, "super_simple_longer"])
        # q_len += len(q)

    # avg_q_len = q_len / n
    # print(f'Average question length: {avg_q_len}')