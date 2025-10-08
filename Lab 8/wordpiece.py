from indicnlp.tokenize import indic_tokenize

ITR = 20
test_text = "The cat is chasing the dog quietly."

def read_sentences(filepath):
    with open(filepath, encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]  # strings joiye as list ma replace method nai hoy

input_sentences = read_sentences("input.txt")

tokens = []
for sentence in input_sentences:
    tokens.extend(indic_tokenize.trivial_tokenize(sentence, lang='gu'))

vocab = list(set(tokens))

def get_stats(vocab):
    pairs = {}
    for word in vocab:
        symbols = word.split()
        for i in range(len(symbols)-1):
            pair = (symbols[i], symbols[i+1])
            if pair not in pairs:
                pairs[pair] = 0
            pairs[pair] += 1
    return pairs

def find_merge(pairs):
    total_counts = sum(pairs.values())  # total number of bigrams
    counts = {}
    for (x, y), freq in pairs.items():
        counts[x] = counts.get(x, 0) + freq
        counts[y] = counts.get(y, 0) + freq

    best_pair = None
    best_score = float('-inf')

    for (x, y), freq in pairs.items():
        p_xy = freq / total_counts
        p_x = counts[x] / total_counts
        p_y = counts[y] / total_counts

        score = p_xy / (p_x * p_y)

        if score > best_score:
            best_score = score
            best_pair = (x, y)

    return best_pair, best_score

merged = []

for i in range(ITR):
    pairs = get_stats(vocab)
    if not pairs:
        break  # nothing to merge
    best_pair, _ = find_merge(pairs)
    if best_pair is None:
        break  # avoid adding None
    vocab.append(best_pair)
    merged.append(best_pair)


# now just do the splitting based on the thing that if the splitting is from middle then use ## as prefix
# example for a word "thesis" we will write "the ##s ##i ##s"
def wordpiece_tokenize(sentence, vocab):
    tokens = indic_tokenize.trivial_tokenize(sentence, lang='gu')
    final_tokens = []

    for word in tokens:
        word = word.lower()
        sub_tokens = []
        i = 0
        while i < len(word):
            found = False
            # longest possible substring from vocab
            for j in range(len(word), i, -1):
                sub = word[i:j]
                if sub in vocab:
                    if i == 0:
                        sub_tokens.append(sub)
                    else:
                        sub_tokens.append('##' + sub)
                    i = j
                    found = True
                    break
            if not found:  # if nothing matched, split char-wise
                sub_tokens.append('##' + word[i])
                i += 1
        final_tokens.extend(sub_tokens)

    return final_tokens

test_tokens = wordpiece_tokenize(test_text, vocab)
print("\nWordPiece tokens for test sentence:")
print(test_tokens)