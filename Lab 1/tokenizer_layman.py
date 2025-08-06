# need to make a word and sentence tokenizer
# tokenize all into words
# tokenize punctuations, URLs, numbers, mail ids and dates
# save the tokenized data into a separate file
# Find total number of sentences, words, charachters, no. of words per sentence
# average no. of chars per word, TTR
# from datasets import load_dataset
# This is for Gujarati language text processing
left, right = 0, 0

# dataset = load_dataset("ai4bharat/IndicCorpV2", "indiccorp_v2", data_dir="data/guj_Gujr")
# for i, example in enumerate(dataset):
#     print(example)
#     if i >= 4:
#         break

def check_punctuation(char):
    return char in ['.', ',', '!', '?', ';', ':', '-', '(', ')', '[', ']', '{', '}', '"', "'", '“', '”', '‘', '’']

def check_url(word):
    # we can't write // or / or . as they will already be a part of other word
    return word.startswith("http") or word.startswith("https") or word.startswith("www")

def check_email(word):
    return "@" in word and "." in word and not word.startswith("http://") and not word.startswith("https://")

def check_number(word):
    return word.isdigit() or (word.replace('.', '', 1).isdigit() and word.count('.') < 2)

def check_date(word):
    # it is a simple date check for formats like dd/mm/yyyy, mm/dd/yyyy, yyyy-mm-dd
    return (len(word) == 10 and (word[2] == '/' or word[2] == '-') and (word[5] == '/' or word[5] == '-')) or \
           (len(word) == 7 and word[2] == '-' and word[5] == '-')

def good_splitter(text):
    global left, right
    # in priority before punctuations we need to check for URLs, Emails and Dates
    # First i am checking for URLs
    if check_url(word):
        # if this word is a URL means next few words are part of the URL
        while(right < len(text) and right != '.'):
            # but this . can be the start of the URL also so previous word is to be checked, if the previous 
            # word is http or https or www then continue finding the '.
            right += 1
        
        at_start = False
        if text[right] == '.':
            if fetch_prev_word(word) in ['http', 'https', 'www']:
                right += 1
                at_start = True
        
        if at_start:
            while(right < len(text) and right != '.'):
                right += 1

        # we came till the end of the URL but the domain name is not included yet
        while(right < len(text) and text[right] != ' '):
            right += 1
        return [text[left:right]]

    # Now i am checking for Emails
    if check_email(text):
        # if this word is an email means previous 1 word and next 3 words are part of the email
        # like it is detecting '@' symbol so previous word is the username and next 3 words are 'gmail', '.' , 'com'
        while(left > 0 and text[left-1] != ' '):
            left -= 1
        while(right < len(text) and text[right] != ' '):
            right += 1
        return [text[left:right]]
    
    # now i am checking for Dates
    if check_date(text):
        # if this word is a date 
        pass

    return [text[left:right]]

    # Now i am checking for Emails
    if check_email(text):
        # if this word is an email means previous 1 word and next 3 words are part of the email
        # like it is detecting '@' symbol so previous word is the username and next 3 words are 'gmail', '.' , 'com'
        while(left > 0 and text[left-1] != ' '):
            left -= 1
        while(right < len(text) and text[right] != ' '):
            right += 1

data = []
with open("gu.txt", "r", encoding="utf-8") as f:
    text = f.read()
    data += good_splitter(text)

print(data)

