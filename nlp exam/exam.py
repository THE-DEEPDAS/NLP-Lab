# pmi for bigram
# pmi = p(x, y) / p(x) * p(y)
# p(x, y) = c(x, y) / c(x) * c(y)
# p(z) = c(z) / N
from collections import defaultdict

with open("input.txt", encoding="utf-8") as f:
    text = f.read()

bigram = defaultdict()
unigram = defaultdict()

# as it is english i am not applying crazyy tokenization
words = text.lower().split()
total = 0

for word in words:
    unigram[word] = 0

for word in words:
    unigram[word] += 1
    total += 1

for i in range(total - 1):
    bigram_ = tuple({words[i], words[i + 1]})
    bigram[bigram_] = 0

for i in range(total - 1):
    bigram_ = tuple({words[i], words[i + 1]})
    bigram[bigram_] += 1

for i in range(total - 1):
    numerator = bigram[tuple({words[i], words[i + 1]})] / (unigram[words[i]] * unigram[words[i + 1]])
    denominator = unigram[words[i]] * unigram[words[i + 1]] / total
    denominator = denominator / total
    if denominator != 0:
        print(f"P({words[i]}, {words[i + 1]}) = {numerator / denominator}")