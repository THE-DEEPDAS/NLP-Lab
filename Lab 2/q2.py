import re
from typing import Dict, List, Tuple, Optional

class NounMorphologyFST:
    def __init__(self, brown_nouns_file: str = None):
        self.valid_nouns = set()
        self.irregular_plurals = {
            # i had to handle some common irregular nouns separately
            'child': 'children',
            'man': 'men',
            'woman': 'women',
            'person': 'people',
            'foot': 'feet',
            'tooth': 'teeth',
            'mouse': 'mice',
            'goose': 'geese',
            'ox': 'oxen',
            'sheep': 'sheep',
            'deer': 'deer',
            'fish': 'fish',
            'series': 'series',
            'species': 'species',
            'datum': 'data',
            'criterion': 'criteria',
            'phenomenon': 'phenomena',
            'analysis': 'analyses',
            'basis': 'bases',
            'crisis': 'crises',
            'thesis': 'theses'
        }
        
        # Reverse mapping for plural to singular
        self.irregular_singulars = {v: k for k, v in self.irregular_plurals.items()}
        
        if brown_nouns_file:
            with open(brown_nouns_file, 'r', encoding='utf-8') as f:
                for line in f:
                    noun = line.strip().lower()
                    if noun:
                        self.valid_nouns.add(noun)
            print(f"Loaded {len(self.valid_nouns)} nouns from Brown corpus")
    
    def is_valid_noun(self, word: str) -> bool:
        word = word.lower()
        
        if self.valid_nouns:
            return word in self.valid_nouns
        
        # this is just in case we don't have a corpus loaded
        if len(word) < 2:
            return False
        if word in ['the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'be', 'been', 'being']:
            return False
        if word.endswith(('ing', 'ed', 'ly')) and not word.endswith(('ring', 'king', 'wing', 'thing')):
            return False
        
        return True
    
    def apply_e_insertion_rule(self, word: str) -> str:
        # e is added after -s, -z, -x, -ch, -sh before -s is added
        # watch -> watches, fox -> foxes
        if word.endswith(('s', 'z', 'x', 'ch', 'sh')):
            return word + 'es'
        return word + 's'
    
    def apply_y_replacement_rule(self, word: str) -> str:
        # -y changes to -ie before -s
        # try -> tries
        if word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
            return word[:-1] + 'ies'
        return word + 's'
    
    def apply_s_addition_rule(self, word: str) -> str:
        # -s is added at the end
        # bag -> bags
        return word + 's'
    
    def get_plural_form(self, singular: str) -> str:
        if singular.lower() in self.irregular_plurals:
            return self.irregular_plurals[singular.lower()]
        
        # this is most specific so doing this 1st
        if singular.endswith(('s', 'z', 'x', 'ch', 'sh')):
            return self.apply_e_insertion_rule(singular)
        
        if singular.endswith('y') and len(singular) > 1 and singular[-2] not in 'aeiou':
            return self.apply_y_replacement_rule(singular)
        
        return self.apply_s_addition_rule(singular) # kai nai to aa em
    
    def get_singular_form(self, plural: str) -> str:
        if plural.lower() in self.irregular_singulars:
            return self.irregular_singulars[plural.lower()]
        
        if plural.endswith('ies') and len(plural) > 3:
            singular = plural[:-3] + 'y'
            return singular
        
        if plural.endswith('es') and len(plural) > 2:
            potential_singular = plural[:-2]
            if potential_singular.endswith(('s', 'z', 'x', 'ch', 'sh')):
                return potential_singular
        
        if plural.endswith('s') and len(plural) > 1:
            return plural[:-1]
        
        return plural
    
    def analyze_word(self, word: str) -> str:
        word = word.strip().lower()
        
        if not word:
            return "Invalid Word"
        
        if word in self.irregular_plurals:
            plural = self.irregular_plurals[word]
            if self.is_valid_noun(word):
                return f"{word} = {word}+N+SG"
            else:
                return "Invalid Word"
        
        if word in self.irregular_singulars:
            singular = self.irregular_singulars[word]
            if self.is_valid_noun(singular):
                return f"{word} = {singular}+N+PL"
            else:
                return "Invalid Word"
        
        # assume it's singular and try to check this
        if self.is_valid_noun(word):
            plural = self.get_plural_form(word)
            return f"{word} = {word}+N+SG"
        
        # now if that didn't work then try to derive singular from potential plural
        potential_singular = self.get_singular_form(word)
        if potential_singular != word and self.is_valid_noun(potential_singular):
            return f"{word} = {potential_singular}+N+PL"
        
        return "Invalid Word"
    
    def process_corpus(self, words: List[str]) -> Dict[str, str]:
        results = {}
        for word in words:
            results[word] = self.analyze_word(word)
        return results
    
    def demonstrate_rules(self):
        examples = [
            'fox', 'foxes', 'watch', 'watches', 'class', 'classes',
            'try', 'tries', 'baby', 'babies', 'city', 'cities',
            'bag', 'bags', 'cat', 'cats', 'house', 'houses',
            'child', 'children', 'man', 'men', 'mouse', 'mice',
            'hanasisn', 'qwerty'
        ]
        
        for word in examples:
            analysis = self.analyze_word(word)
            print(f"{word:15} -> {analysis}")

brown_nouns_file = "brown_nouns.txt"
fst = NounMorphologyFST(brown_nouns_file)
fst.demonstrate_rules()

while True:
    word = input("\nEnter a word to analyze: ").strip()
    if word.lower() == 'quit':
        break
    if word:
        result = fst.analyze_word(word)
        print(f"My Result: {result}")