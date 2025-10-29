import re
import json
from collections import Counter

MERGE_STEPS = 32000
VOCAB_SIZE = 32000

def read_corpus(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def get_word_freqs(corpus):
    word_freqs = Counter()
    for line in corpus:
        words = re.findall(r'\w+', line.lower())
        for word in words:
            word_freqs[word] += 1
    return word_freqs

def get_stats(vocab):
    pairs = Counter()
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pairs[(symbols[i], symbols[i + 1])] += freq
    return pairs

def merge_vocab(pair, vocab):
    new_vocab = {}
    bigram = re.escape(' '.join(pair))
    p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
    for word in vocab:
        new_word = p.sub(''.join(pair), word)
        new_vocab[new_word] = vocab[word]
    return new_vocab

# read data
corpus = read_corpus('../train.txt')
print(f"Corpus size: {len(corpus)} sentences")

# get word frequencies and prepare vocab
word_freqs = get_word_freqs(corpus)
vocab = {}
for word, freq in word_freqs.items():
    vocab[' '.join(word) + ' </w>'] = freq

print(f"Initial vocab size: {len(set(' '.join(vocab.keys()).split()))}")

# perform merges
merges = []
for i in range(MERGE_STEPS):
    if i % 1000 == 0:
        print(f"Merge {i}/{MERGE_STEPS}")
    
    pairs = get_stats(vocab)
    if not pairs:
        break
    
    best_pair = pairs.most_common(1)[0][0]
    vocab = merge_vocab(best_pair, vocab)
    merges.append(best_pair)
    
    # check vocab size
    all_symbols = set(' '.join(vocab.keys()).split())
    if len(all_symbols) >= VOCAB_SIZE:
        print(f"Reached vocab size {len(all_symbols)} at step {i}")
        break

# save model
final_vocab = set(' '.join(vocab.keys()).split())
model_data = {
    'vocab': list(final_vocab),
    'merges': merges,
    'word_vocab': vocab
}

with open('bpe_model.json', 'w', encoding='utf-8') as f:
    json.dump(model_data, f, ensure_ascii=False)

def bpe_encode(text, merges):
    words = re.findall(r'\w+', text.lower())
    encoded = []
    
    for word in words:
        word_tokens = list(word) + ['</w>']
        word_str = ' '.join(word_tokens)
        
        for pair in merges:
            bigram = re.escape(' '.join(pair))
            p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
            word_str = p.sub(''.join(pair), word_str)
        
        encoded.extend(word_str.split())
    
    return encoded

# test encoding
test_sentences = [
    "જિલ્લા ફોરમમાં, જેની હકૂમતની અંદર.",
    "તમારા એમ્પ્લોયરનું નામ, તમારા કાર્યાલયનું સરનામું, કાર્યાલય ટેલિફોન નંબર, તમે કેટલા લાંબા સમયથી આ કંપની સાથે કાર્યરત થઈ ગયા છો, અને તમારા વ્યવસાયની જાણ કરો.",
    "ભાઈ, જુઓ છો ને!"
]

print(f"\nFinal vocab size: {len(final_vocab)}")
print(f"Number of merges: {len(merges)}")

print("\nBPE Encoding Examples:")
for sentence in test_sentences:
    encoded = bpe_encode(sentence, merges)
    print(f"Original: {sentence}")
    print(f"Encoded: {encoded}")
    print()

print("Model saved to bpe_model.json")
