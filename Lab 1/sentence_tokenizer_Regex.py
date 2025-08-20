import re

def gujarati_sentence_tokenizer(text):
    # Patterns to protect
    url_pattern = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}0-9(\b([-a-zA-Z)@:%_\+.~#?&//=]*)'
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?$'
    date_pattern = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s*(જાન્યુઆરી|ફેબ્રુઆરી|માર્ચ|એપ્રિલ|મે|જૂન|જુલાઈ|ઑગસ્ટ|સપ્ટેમ્બર|ઑક્ટોબર|નવેમ્બર|ડિસેમ્બર)\s*\d{2,4}'
    
    # Protect URLs, emails, dates, ellipsis by replacing them with placeholders
    protected = []
    def protect(match):
        protected.append(match.group(0))
        return f"__PROTECTED_{len(protected)-1}__"

    # Protect ellipsis (three dots)
    text = re.sub(r'\.\.\.', protect, text)
    text = re.sub(url_pattern, protect, text)
    text = re.sub(email_pattern, protect, text)
    text = re.sub(date_pattern, protect, text)


    # Protect abbreviations (e.g., Dr., Mr., etc. and Gujarati abbreviations)
    abbrs = [
        r'Dr\.', r'Mr\.', r'Mrs\.', r'Ms\.', r'Prof\.', r'Sr\.', r'Jr\.', r'St\.', r'vs\.', r'etc\.', r'e\.g\.', r'i\.e\.', r'a\.m\.', r'p\.m\.',
        r'એલ\.સી\.બી\.', r'પી\.એસ\.આઇ\.', r'શ્રી\.', r'શ્રીમતી\.', r'કું\.', r'શ્રીમ\.', r'ડૉ\.', r'પ્રો\.', r'સ્વ\.'
    ]
    abbr_pattern = r'(' + '|'.join(abbrs) + r')'
    text = re.sub(abbr_pattern, protect, text)

    # Protect numbers (Gujarati/English) followed by dot (e.g., 18. or ૧૮.)
    num_dot_pattern = r'(?:\d+|[\u0AE6-\u0AEF]+)\.'
    text = re.sub(num_dot_pattern, protect, text)

    # Protect words with matra followed by dot (e.g., "તા.")
    guj_word_matra_dot = r'([\u0A80-\u0AFF]+[\u0ABE-\u0ACC\u0A81-\u0A83\u0ACD]+)\.'
    text = re.sub(guj_word_matra_dot, protect, text)

    # Use a more reliable method to split sentences
    # Split at sentence ending punctuation
    sentence_end_pattern = r'([\.!?।\u0964])\s+'
    
    # Split the text but keep the punctuation
    parts = re.split(sentence_end_pattern, text)
    
    sentences = []
    for i in range(0, len(parts)-1, 2):
        if i+1 < len(parts):
            sentence = parts[i] + parts[i+1]
        else:
            sentence = parts[i]
        
        # Restore protected items
        for idx, item in enumerate(protected):
            sentence = sentence.replace(f"__PROTECTED_{idx}__", item)
        
        sentence = sentence.strip()
        if sentence:
            sentences.append(sentence)
    
    # Handle the last part if there's no ending punctuation
    if len(parts) % 2 == 1 and parts[-1].strip():
        last = parts[-1].strip()
        # Restore protected items
        for idx, item in enumerate(protected):
            last = last.replace(f"__PROTECTED_{idx}__", item)
        if last:
            sentences.append(last)

    # Merge sentences with less than 3 words with previous sentence
    merged = []
    for s in sentences:
        if merged and len(s.split()) < 3:
            merged[-1] = merged[-1].rstrip() + ' ' + s
        else:
            merged.append(s)
    
    return merged

class ChunkedTextGenerator:
    def __init__(self, file_path, char_limit=5000000):
        self.file_path = file_path
        self.char_limit = char_limit

    def __iter__(self):
        buffer = []
        total_chars = 0
        with open(self.file_path, encoding="utf-8", errors="ignore") as infile:
            for line in infile:
                buffer.append(line)
                total_chars += len(line)
                if total_chars > self.char_limit:
                    yield "".join(buffer)
                    buffer = []
                    total_chars = 0
            if buffer:
                yield "".join(buffer)

# --- Metrics calculation for large output file (streaming, memory efficient) ---
def calculate_metrics_from_file(filename, metrics_filename):
    total_sentences = 0
    total_words = 0
    total_chars = 0
    unique_words = set()
    with open(filename, encoding="utf-8") as f:
        for line in f:
            sentence = line.strip()
            if not sentence:
                continue
            total_sentences += 1
            words = sentence.split()
            total_words += len(words)
            total_chars += len(sentence)
            unique_words.update(words)
    words_per_sentence = total_words / total_sentences if total_sentences else 0
    avg_chars_per_word = total_chars / total_words if total_words else 0
    ttr = len(unique_words) / total_words if total_words else 0
    with open(metrics_filename, "w", encoding="utf-8") as m:
        m.write(f"Total sentences: {total_sentences}\n")
        m.write(f"Total words: {total_words}\n")
        m.write(f"Total characters: {total_chars}\n")
        m.write(f"Words per sentence: {words_per_sentence:.2f}\n")
        m.write(f"Average characters per word: {avg_chars_per_word:.2f}\n")
        m.write(f"Type-Token Ratio (TTR): {ttr:.4f}\n")

if __name__ == "__main__":
    with open("gu.txt", encoding="utf-8") as f:
        text = f.read()
    sentences = gujarati_sentence_tokenizer(text)
    # Write sentences to a new file, each on a new line
    with open("gu_sentences.txt", "w", encoding="utf-8") as out:
        for s in sentences:
            out.write(s + "\n")
    # --- Metrics calculation ---
    total_sentences = len(sentences)
    total_words = sum(len(s.split()) for s in sentences)
    total_chars = sum(len(s) for s in sentences)
    words_per_sentence = total_words / total_sentences if total_sentences else 0
    avg_chars_per_word = total_chars / total_words if total_words else 0
    # TTR for sentence tokenizer: unique words divided by total words
    all_words = []
    for s in sentences:
        all_words.extend(s.split())
    ttr = len(set(all_words)) / total_words if total_words else 0
    with open("gu_sentences_metrics.txt", "w", encoding="utf-8") as m:
        m.write(f"Total sentences: {total_sentences}\n")
        m.write(f"Total words: {total_words}\n")
        m.write(f"Total characters: {total_chars}\n")
        m.write(f"Words per sentence: {words_per_sentence:.2f}\n")
        m.write(f"Average characters per word: {avg_chars_per_word:.2f}\n")
        m.write(f"Type-Token Ratio (TTR): {ttr:.4f}\n")

    # --- Hugging Face IndicCorpV2 Gujarati Dataset Tokenization ---
    chunk_gen = ChunkedTextGenerator("indiccorp_gu.txt", char_limit=5000000)
    with open("gu_sentences_indic_corp.txt", "w", encoding="utf-8") as outfile:
        for text_chunk in chunk_gen:
            sentences = gujarati_sentence_tokenizer(text_chunk)
            for s in sentences:
                outfile.write(s + "\n\n")
    calculate_metrics_from_file("gu_sentences_indic_corp.txt", "gu_sentences_indic_corp_metrics.txt")
