from collections import Counter
import json

ITR = 32000
VOCAB_SIZE = 32000
test_text = "છોકરો બિલાડી સાથે રમે છે અને કૂતરો બગીચામાં દોડે છે"

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
        elif char.isspace():
            if current_word:
                tokens.append(''.join(current_word))
                current_word = []
        elif char.isalnum():
            current_word.append(char)
        else:
            if current_word:
                tokens.append(''.join(current_word))
                current_word = []
    
    if current_word:
        tokens.append(''.join(current_word))
    
    return tokens

def split_gujarati_word(word):
    chars = []
    i = 0
    while i < len(word):
        char = word[i]
        char_code = ord(char)
        
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

def read_sentences(filepath):
    with open(filepath, encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]

input_sentences = read_sentences("train_sampled.txt")

# collect tokens from corpus
tokens = []
for sentence in input_sentences:
    sentence_tokens = gujarati_tokenize(sentence)
    for token in sentence_tokens:
        if any(ord(c) in GUJARATI_CHARS for c in token):
            tokens.append(token)

# build word frequencies
word_freqs = Counter(tokens)

# build initial symbol lists for each distinct word
word_symbols = {}
for w in set(tokens):
    if not w:
        continue
    chars = split_gujarati_word(w)
    if len(chars) == 1:
        word_symbols[w] = [chars[0]]
    else:
        word_symbols[w] = [chars[0]] + [f"##{c}" for c in chars[1:]]

def get_pair_counts(word_symbols, word_freqs):
    pairs = Counter()
    for word, symbols in word_symbols.items():
        freq = word_freqs[word]
        for i in range(len(symbols) - 1):
            pairs[(symbols[i], symbols[i + 1])] += freq
    return pairs

def find_best_merge(pairs, word_symbols, word_freqs):
    # WordPiece uses probability-based scoring: P(xy) / (P(x) * P(y))
    symbol_counts = Counter()
    
    # count individual symbols weighted by word frequency
    for word, symbols in word_symbols.items():
        freq = word_freqs[word]
        for symbol in symbols:
            symbol_counts[symbol] += freq
    
    total_pairs = sum(pairs.values())
    total_symbols = sum(symbol_counts.values())
    
    best_pair = None
    best_score = float('-inf')
    
    for (x, y), freq in pairs.items():
        if freq > 1:  # only consider pairs that appear more than once
            p_xy = freq / total_pairs if total_pairs > 0 else 0
            p_x = symbol_counts[x] / total_symbols if total_symbols > 0 else 0
            p_y = symbol_counts[y] / total_symbols if total_symbols > 0 else 0
            
            # WordPiece probability score: P(xy) / (P(x) * P(y))
            if p_x > 0 and p_y > 0:
                score = p_xy / (p_x * p_y)
                if score > best_score:
                    best_score = score
                    best_pair = (x, y)
    
    return best_pair, best_score

def merge_symbols(pair, word_symbols):
    symbol1, symbol2 = pair
    y_clean = symbol2[2:] if symbol2.startswith('##') else symbol2
    new_symbol = symbol1 + y_clean
    
    new_word_symbols = {}
    for word, symbols in word_symbols.items():
        new_symbols = []
        i = 0
        while i < len(symbols):
            if i < len(symbols) - 1 and symbols[i] == symbol1 and symbols[i + 1] == symbol2:
                new_symbols.append(new_symbol)
                i += 2
            else:
                new_symbols.append(symbols[i])
                i += 1
        new_word_symbols[word] = new_symbols
    
    return new_word_symbols, new_symbol

# perform merges using WordPiece probability scoring
vocab_symbols = set()
for symbols in word_symbols.values():
    vocab_symbols.update(symbols)

print(f"Initial vocab size: {len(vocab_symbols)}")

merged_pairs = []
for i in range(ITR):
    if i % 1000 == 0:
        print(f"Merge {i}/{ITR}, vocab size: {len(vocab_symbols)}")
    
    pairs = get_pair_counts(word_symbols, word_freqs)
    if not pairs:
        print(f"No more pairs to merge at step {i}")
        break
    
    if len(vocab_symbols) >= VOCAB_SIZE:
        print(f"Reached vocab size {len(vocab_symbols)} at step {i}")
        break
    
    # WordPiece: select pair with highest probability score
    best_pair, score = find_best_merge(pairs, word_symbols, word_freqs)
    if best_pair is None:
        print(f"No valid pair found at step {i}")
        break
    
    word_symbols, new_symbol = merge_symbols(best_pair, word_symbols)
    merged_pairs.append((best_pair, new_symbol))
    vocab_symbols.add(new_symbol)

print(f"Training completed. Total merges: {len(merged_pairs)}")

final_vocab = vocab_symbols

# save model
model_data = {
    'vocab': list(final_vocab),
    'merges': merged_pairs,
    'word_symbols': word_symbols
}
with open('wordpiece_model.json', 'w', encoding='utf-8') as f:
    json.dump(model_data, f, ensure_ascii=False)

def wordpiece_tokenize(sentence, final_vocab):
    tokens = gujarati_tokenize(sentence)
    out = []
    for word in tokens:
        w = word.lower()
        if len(w) == 0 or not any(ord(c) in GUJARATI_CHARS for c in w):
            continue
        
        word_pieces = []
        i = 0
        while i < len(w):
            matched = None
            # try longest possible substring starting at i (greedy longest-first matching)
            for j in range(len(w), i, -1):
                candidate = w[i:j]
                if candidate in final_vocab:
                    matched = candidate
                    break
                elif i > 0 and f"##{candidate}" in final_vocab:
                    matched = f"##{candidate}"
                    break
            
            if matched is None:
                # fallback: single character with ## prefix if not at start
                if i == 0:
                    matched = w[i]
                else:
                    matched = f"##{w[i]}"
                i += 1
            else:
                # advance by actual character length (handle ## prefix correctly)
                advance = len(matched[2:]) if matched.startswith('##') else len(matched)
                i += advance
            
            word_pieces.append(matched)
        out.extend(word_pieces)
    return out

test_tokens = wordpiece_tokenize(test_text, final_vocab)
print("\nWordPiece tokens for test sentence:")
print(test_tokens)

print(f"\nFinal vocab size: {len(final_vocab)}")
print(f"Number of merges: {len(merged_pairs)}")
print("Model saved to wordpiece_model.json")