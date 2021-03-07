import random

def make_q_a(num1, num2):
	add = (random.random() >= 0.5)
	q = "{}{}{}".format(num1, "+" if add else "-", num2)
	a = "{}".format(num1 + num2 if add else num1 - num2)
	return "{}\t{}\t1\tsuper_simple_add_sub".format(q, a)

def pickNum():
    digits = random.randint(1, 9)
    return random.randint(10**(digits - 1) - 1, 10**digits - 1)


with open("raw_data_tsv/super_simple_add_subtract_larger_test.tsv", "w") as fout:
	for i in range(10000):
                num1 = pickNum()
                num2 = pickNum()
                print(make_q_a(num1, num2), file=fout)
