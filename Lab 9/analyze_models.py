import json
from collections import Counter

def analyze_bpe_model():
    with open('bpe_model.json', 'r', encoding='utf-8') as f:
        model = json.load(f)
    
    print("BPE MODEL ANALYSIS")
    print("="*50)
    print(f"Total vocabulary size: {len(model['vocab'])}")
    print(f"Total merges performed: {len(model['merges'])}")
    
    # analyze merge patterns
    merge_lengths = []
    for pair in model['merges']:
        merged = ''.join(pair)
        merge_lengths.append(len(merged))
    
    print(f"Average merge length: {sum(merge_lengths)/len(merge_lengths):.2f}")
    print(f"Max merge length: {max(merge_lengths)}")
    
    # show some sample merges
    print("\nFirst 20 merges:")
    for i, pair in enumerate(model['merges'][:20]):
        print(f"  {i+1:2d}. {pair[0]} + {pair[1]} = {''.join(pair)}")
    
    print("\nLast 20 merges:")
    for i, pair in enumerate(model['merges'][-20:], len(model['merges'])-19):
        print(f"  {i:2d}. {pair[0]} + {pair[1]} = {''.join(pair)}")
    
    # analyze vocabulary
    vocab_lengths = [len(token.replace('</w>', '')) for token in model['vocab']]
    print(f"\nVocabulary token lengths:")
    print(f"  Average: {sum(vocab_lengths)/len(vocab_lengths):.2f}")
    print(f"  Max: {max(vocab_lengths)}")
    print(f"  Min: {min(vocab_lengths)}")
    
    # show longest tokens
    longest_tokens = sorted(model['vocab'], key=lambda x: len(x.replace('</w>', '')), reverse=True)[:10]
    print(f"\nLongest BPE tokens:")
    for i, token in enumerate(longest_tokens, 1):
        print(f"  {i:2d}. {token} (length: {len(token.replace('</w>', ''))})")

def analyze_wordpiece_model():
    with open('wordpiece_model.json', 'r', encoding='utf-8') as f:
        model = json.load(f)
    
    print("\n\nWORDPIECE MODEL ANALYSIS")
    print("="*50)
    print(f"Total vocabulary size: {len(model['vocab'])}")
    print(f"Total merges performed: {len(model['merges'])}")
    
    # analyze merge patterns
    merge_lengths = []
    for (pair, new_sym) in model['merges']:
        merge_lengths.append(len(new_sym.replace('##', '')))
    
    print(f"Average merged token length: {sum(merge_lengths)/len(merge_lengths):.2f}")
    print(f"Max merged token length: {max(merge_lengths)}")
    
    # show some sample merges
    print("\nFirst 20 merges:")
    for i, ((s1, s2), new_sym) in enumerate(model['merges'][:20]):
        print(f"  {i+1:2d}. {s1} + {s2} = {new_sym}")
    
    print("\nLast 20 merges:")
    for i, ((s1, s2), new_sym) in enumerate(model['merges'][-20:], len(model['merges'])-19):
        print(f"  {i:2d}. {s1} + {s2} = {new_sym}")
    
    # analyze vocabulary
    vocab_lengths = [len(token.replace('##', '')) for token in model['vocab']]
    print(f"\nVocabulary token lengths:")
    print(f"  Average: {sum(vocab_lengths)/len(vocab_lengths):.2f}")
    print(f"  Max: {max(vocab_lengths)}")
    print(f"  Min: {min(vocab_lengths)}")
    
    # show longest tokens
    longest_tokens = sorted(model['vocab'], key=lambda x: len(x.replace('##', '')), reverse=True)[:10]
    print(f"\nLongest WordPiece tokens:")
    for i, token in enumerate(longest_tokens, 1):
        print(f"  {i:2d}. {token} (length: {len(token.replace('##', ''))})")
    
    # count ## tokens vs regular tokens
    continuation_tokens = sum(1 for token in model['vocab'] if token.startswith('##'))
    regular_tokens = len(model['vocab']) - continuation_tokens
    print(f"\nToken types:")
    print(f"  Regular tokens: {regular_tokens}")
    print(f"  Continuation tokens (##): {continuation_tokens}")

if __name__ == "__main__":
    analyze_bpe_model()
    analyze_wordpiece_model()
