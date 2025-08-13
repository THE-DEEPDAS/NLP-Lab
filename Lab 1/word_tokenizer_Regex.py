import re

def gujarati_word_tokenizer(text):
    url_pattern = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}0-9(\b([-a-zA-Z)@:%_\+.~#?&//=]*)'
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?$'
    date_pattern = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s*[જાન્યુઆરી|ફેબ્રુઆરી|માર્ચ|એપ્રિલ|મે|જૂન|જુલાઈ|ઑગસ્ટ|સપ્ટેમ્બર|ઑક્ટોબર|નવેમ્બર|ડિસેમ્બર]+\s*\d{2,4}'
    num_pattern = r'(?:[\d\u0AE6-\u0AEF]+(?:[\.,][\d\u0AE6-\u0AEF]+)+)'
    eng_num_dot_pattern = r'\d+\.'
    guj_num_pattern = r'[\u0AE6-\u0AEF]+'
    eng_num_pattern = r'\d+'
    guj_word_pattern = r'[\u0A80-\u0AFF]+(?:[\u0ABE-\u0ACC\u0A81-\u0A83\u0ACD]*)'
    punct_pattern = r'[\.।\u0964,!?…]' # includes . | danda | gujarati full stop | , ! ? …
    ellipsis_pattern = r'\.\.\.'

    combined_pattern = f'({url_pattern})|({email_pattern})|({date_pattern})|({eng_num_dot_pattern})|({num_pattern})|({ellipsis_pattern})|({punct_pattern})|({guj_num_pattern})|({eng_num_pattern})|({guj_word_pattern})'
    words = [w for w in re.findall(combined_pattern, text)]
    flat_words = []
    for tup in words:
        for w in tup:
            if w:
                flat_words.append(w)
    return flat_words

def process_in_chunks(input_file, output_file, tokenizer, chunk_size=1024 * 1024 * 100):  # 100 MB chunks
    buffer = ""

    with open(input_file, "r", encoding="utf-8", errors="ignore") as infile, \
         open(output_file, "w", encoding="utf-8") as outfile:

        while True:
            chunk = infile.read(chunk_size)
            if not chunk:
                break

            buffer += chunk

            if len(buffer) > chunk_size:
                words = tokenizer(buffer)
                for word in words:
                    if re.match(r'^\d+\.$', word):
                        outfile.write(word + ' ')
                    elif word in ['.', '।', '\u0964', '…', '...']:
                        outfile.write(word + '\n')
                    else:
                        outfile.write(word + ' ')
                buffer = ""  

        if buffer.strip():
            words = tokenizer(buffer)
            for word in words:
                if re.match(r'^\d+\.$', word):
                    outfile.write(word + ' ')
                elif word in ['.', '।', '\u0964', '…', '...']:
                    outfile.write(word + '\n')
                else:
                    outfile.write(word + ' ')

if __name__ == "__main__":
    process_in_chunks("indiccorp_gu.txt", "indiccorp_gu_words.txt", gujarati_word_tokenizer)
    sentence_endings = ['.', '।', '\u0964', '…', '...']
    total_words = 0
    total_chars = 0
    unique_words = set()
    num_sentences = 0
    with open("indiccorp_gu_words.txt", encoding="utf-8") as f:
        for line in f:
            words_in_line = line.strip().split()
            total_words += len(words_in_line)
            total_chars += sum(len(w) for w in words_in_line)
            unique_words.update(words_in_line)
            if any(p in line for p in sentence_endings):
                num_sentences += 1
    words_per_sentence = total_words / num_sentences if num_sentences else 0
    avg_chars_per_word = total_chars / total_words if total_words else 0
    ttr = len(unique_words) / total_words if total_words else 0
    with open("indiccorp_gu_words_metrics.txt", "w", encoding="utf-8") as m:
        m.write(f"Total words: {total_words}\n")
        m.write(f"Total characters: {total_chars}\n")
        m.write(f"Number of sentences (approx): {num_sentences}\n")
        m.write(f"Words per sentence (approx): {words_per_sentence:.2f}\n")
        m.write(f"Average characters per word: {avg_chars_per_word:.2f}\n")
        m.write(f"Type-Token Ratio (TTR): {ttr:.4f}\n")