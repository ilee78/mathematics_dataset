import random

def make_q_a(num1, num2):
	add = (random.random() >= 0.5)
	q = "{}{}{}".format(num1, "+" if add else "-", num2)
	a = "{}".format(num1 + num2 if add else num1 - num2)
	return "{}\t{}\t1\tsuper_simple_add_sub".format(q, a)


with open("ssas.tsv", "w") as fout:
	for i in range(1000):
		num1 = random.randint(0, 40)
		num2 = random.randint(0, 40)
		print(make_q_a(num1, num2), file=fout)