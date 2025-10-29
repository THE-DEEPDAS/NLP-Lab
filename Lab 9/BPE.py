import re
import json
from collections import Counter

MERGE_STEPS = 32000
VOCAB_SIZE = 32000
GUJARATI_CHARS = set(range(0x0A80, 0x0B00))
GUJARATI_MATRAS = set([0x0ABE, 0x0ABF, 0x0AC0, 0x0AC1, 0x0AC2, 0x0AC3, 0x0AC4, 0x0AC5, 0x0AC7, 0x0AC8, 0x0AC9, 0x0ACB, 0x0ACC])
GUJARATI_VIRAMAS = set([0x0ACD])

def gujarati_tokenize(text):
    tokens = []
    current_word = []
    
    for char in text:
        char_code = ord(char)
        
        if char_code in GUJARATI_CHARS:
            current_word.append(char)
        elif char.isspace(): # space aave to tokens ma add kari devo 
            if current_word:
                tokens.append(''.join(current_word))
                current_word = []
        elif char.isalnum():
            current_word.append(char)
        else:
            if current_word:
                tokens.append(''.join(current_word))
                current_word = []
    
    if current_word: # last ma to add karvanuj che
        tokens.append(''.join(current_word))
    
    return tokens

def split_gujarati_word(word):
    chars = []
    i = 0
    while i < len(word):
        char = word[i]
        
        chars.append(char)
        i += 1
        
        while i < len(word):
            next_char = word[i]
            next_code = ord(next_char)
            if next_code in GUJARATI_MATRAS or next_code in GUJARATI_VIRAMAS:
                chars[-1] += next_char
                i += 1
            else:
                break
    
    return chars

def read_corpus(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def get_word_freqs(corpus):
    word_freqs = Counter()
    for line in corpus:
        words = gujarati_tokenize(line.lower())
        for word in words:
            if any(ord(c) in GUJARATI_CHARS for c in word):
                word_freqs[word] += 1
    return word_freqs

def get_stats(vocab):
    pairs = Counter()
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pairs[(symbols[i], symbols[i + 1])] += freq
    return pairs

def merge_vocab(pair, vocab): # pair is tuple of 2 symbols
    new_vocab = {}
    bigram = re.escape(' '.join(pair)) # space thi join kairi, used escape for handling special chars
    #not preceded by a non-space character and not followed by a non-space character
    p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
    for word in vocab:
        new_word = p.sub(''.join(pair), word)
        new_vocab[new_word] = vocab[word]
    return new_vocab

# read data
corpus = read_corpus('train_sampled.txt')
print(f"Corpus size: {len(corpus)} sentences")
word_freqs = get_word_freqs(corpus)
vocab = {}
for word, freq in word_freqs.items():
    chars = split_gujarati_word(word)
    vocab[' '.join(chars) + ' </w>'] = freq

print(f"Initial vocab size: {len(set(' '.join(vocab.keys()).split()))}")

merges = []
for i in range(MERGE_STEPS):
    if i % 1000 == 0:
        print(f"Merge {i}/{MERGE_STEPS}")
    
    pairs = get_stats(vocab)
    if not pairs:
        print(f"No more pairs to merge at step {i}")
        break
    
    # BPE: select most frequent pair (frequency-based)
    best_pair = pairs.most_common(1)[0][0]
    vocab = merge_vocab(best_pair, vocab)
    merges.append(best_pair)
    
    # check vocabulary size
    all_symbols = set(' '.join(vocab.keys()).split())
    if len(all_symbols) >= VOCAB_SIZE:
        print(f"Reached vocab size {len(all_symbols)} at step {i}")
        break

print(f"Training completed. Total merges: {len(merges)}")

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
    words = gujarati_tokenize(text.lower())
    encoded = []
    
    for word in words:
        if not any(ord(c) in GUJARATI_CHARS for c in word):
            continue
        chars = split_gujarati_word(word)
        word_tokens = chars + ['</w>']
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
    "તમારા એમ્પ્લોયરનું નામ, તમારા કાર્યાલયનું સરનામું.",
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
