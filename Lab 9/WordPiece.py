import re
import json
import math
from collections import Counter, defaultdict

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

def get_pair_scores(word_splits, word_freqs):
    pair_counts = defaultdict(int)
    symbol_counts = defaultdict(int)
    
    for word, symbols in word_splits.items():
        freq = word_freqs[word]
        for symbol in symbols:
            symbol_counts[symbol] += freq
        for i in range(len(symbols) - 1):
            pair = (symbols[i], symbols[i + 1])
            pair_counts[pair] += freq
    
    pair_scores = {}
    total_pairs = sum(pair_counts.values())
    total_symbols = sum(symbol_counts.values())
    
    for pair, count in pair_counts.items():
        if count > 1:
            symbol1, symbol2 = pair
            p_pair = count / total_pairs
            p_symbol1 = symbol_counts[symbol1] / total_symbols
            p_symbol2 = symbol_counts[symbol2] / total_symbols
            
            if p_symbol1 > 0 and p_symbol2 > 0:
                score = p_pair / (p_symbol1 * p_symbol2)
                pair_scores[pair] = score
    
    return pair_scores

def merge_symbols(pair, word_splits):
    symbol1, symbol2 = pair
    y_clean = symbol2[2:] if symbol2.startswith('##') else symbol2
    new_symbol = symbol1 + y_clean
    
    new_word_splits = {}
    for word, symbols in word_splits.items():
        new_symbols = []
        i = 0
        while i < len(symbols):
            if i < len(symbols) - 1 and symbols[i] == symbol1 and symbols[i + 1] == symbol2:
                new_symbols.append(new_symbol)
                i += 2
            else:
                new_symbols.append(symbols[i])
                i += 1
        new_word_splits[word] = new_symbols
    
    return new_word_splits, new_symbol

# read data
corpus = read_corpus('../train.txt')
print(f"Corpus size: {len(corpus)} sentences")

# get word frequencies
word_freqs = get_word_freqs(corpus)

# initialize word splits
word_splits = {}
for word in word_freqs:
    if len(word) <= 1:
        word_splits[word] = [word]
    else:
        word_splits[word] = [word[0]] + [f"##{c}" for c in word[1:]]

# build initial vocab
vocab = set()
for symbols in word_splits.values():
    vocab.update(symbols)

print(f"Initial vocab size: {len(vocab)}")

# perform merges
merges = []
for i in range(MERGE_STEPS):
    if i % 1000 == 0:
        print(f"Merge {i}/{MERGE_STEPS}, vocab size: {len(vocab)}")
    
    pair_scores = get_pair_scores(word_splits, word_freqs)
    if not pair_scores:
        break
    
    if len(vocab) >= VOCAB_SIZE:
        print(f"Reached vocab size {len(vocab)} at step {i}")
        break
    
    best_pair = max(pair_scores, key=pair_scores.get)
    word_splits, new_symbol = merge_symbols(best_pair, word_splits)
    merges.append((best_pair, new_symbol))
    vocab.add(new_symbol)

# save model
model_data = {
    'vocab': list(vocab),
    'merges': merges,
    'word_splits': word_splits
}

with open('wordpiece_model.json', 'w', encoding='utf-8') as f:
    json.dump(model_data, f, ensure_ascii=False)

def wordpiece_encode(text, merges):
    words = re.findall(r'\w+', text.lower())
    encoded = []
    
    for word in words:
        if len(word) <= 1:
            tokens = [word]
        else:
            tokens = [word[0]] + [f"##{c}" for c in word[1:]]
        
        for (symbol1, symbol2), new_symbol in merges:
            new_tokens = []
            i = 0
            while i < len(tokens):
                if i < len(tokens) - 1 and tokens[i] == symbol1 and tokens[i + 1] == symbol2:
                    new_tokens.append(new_symbol)
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            tokens = new_tokens
        
        encoded.extend(tokens)
    
    return encoded

# test encoding
test_sentences = [
    "જિલ્લા ફોરમમાં, જેની હકૂમતની અંદર.",
    "તમારા એમ્પ્લોયરનું નામ, તમારા કાર્યાલયનું સરનામું, કાર્યાલય ટેલિફોન નંબર, તમે કેટલા લાંબા સમયથી આ કંપની સાથે કાર્યરત થઈ ગયા છો, અને તમારા વ્યવસાયની જાણ કરો.",
    "ભાઈ, જુઓ છો ને!"
]

print(f"\nFinal vocab size: {len(vocab)}")
print(f"Number of merges: {len(merges)}")

print("\nWordPiece Encoding Examples:")
for sentence in test_sentences:
    encoded = wordpiece_encode(sentence, merges)
    print(f"Original: {sentence}")
    print(f"Encoded: {encoded}")
    print()

print("Model saved to wordpiece_model.json")
