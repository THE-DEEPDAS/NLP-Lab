import re
from typing import List, Dict

class NounMorphologyStemmer:
    def __init__(self, brown_nouns_file: str = None):
        self.valid_nouns = set()
        self.irregular_plurals = {
            'children': 'child', 'men': 'man', 'women': 'woman', 'people': 'person',
            'feet': 'foot', 'teeth': 'tooth', 'mice': 'mouse', 'geese': 'goose',
            'oxen': 'ox', 'sheep': 'sheep', 'deer': 'deer', 'fish': 'fish',
            'series': 'series', 'species': 'species', 'data': 'datum',
            'criteria': 'criterion', 'phenomena': 'phenomenon',
            'analyses': 'analysis', 'bases': 'basis', 'crises': 'crisis', 'theses': 'thesis'
        }
        self.irregular_singulars = {v: k for k, v in self.irregular_plurals.items()}
        if brown_nouns_file:
            with open(brown_nouns_file, 'r', encoding='utf-8') as f:
                for line in f:
                    noun = line.strip().lower()
                    if noun:
                        self.valid_nouns.add(noun)

    def stem(self, word: str) -> str:
        # Try to get the singular form by removing common plural suffixes
        if word in self.irregular_plurals:
            return self.irregular_plurals[word]
        if word.endswith('ies') and len(word) > 3:
            return word[:-3] + 'y'
        if word.endswith('es') and len(word) > 2:
            if word[:-2].endswith(('s', 'z', 'x', 'ch', 'sh')):
                return word[:-2]
        if word.endswith('s') and len(word) > 1:
            return word[:-1]
        return word

    def analyze_word(self, word: str) -> str:
        word = word.strip().lower()
        if not word:
            return "Invalid Word"
        # First, try to stem the word to get its singular form
        stemmed = self.stem(word)
        # If the original word is in the irregular singulars, it's plural
        if word in self.irregular_singulars:
            if stemmed in self.valid_nouns:
                return f"{word} = {stemmed}+N+PL"
            else:
                return "Invalid Word"
        # If the stemmed word is a valid noun and the original word is not the same as the stemmed, it's plural
        if stemmed in self.valid_nouns and word != stemmed:
            return f"{word} = {stemmed}+N+PL"
        # If the word itself is a valid noun, it's singular
        if word in self.valid_nouns:
            return f"{word} = {word}+N+SG"
        return "Invalid Word"

    def demonstrate_rules(self):
        print("Enter a word to analyze (type 'quit' to exit):")
        while True:
            word = input("\nWord: ").strip()
            if word.lower() == 'quit':
                break
            if word:
                result = self.analyze_word(word)
                print(f"Analysis: {result}")

if __name__ == "__main__":
    brown_nouns_file = "brown_nouns.txt"
    fst = NounMorphologyStemmer(brown_nouns_file)
    fst.demonstrate_rules()
