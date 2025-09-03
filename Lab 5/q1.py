import random
input_path = "F:\\NLP Lab\\Lab 1\\final_sentence_tokenized.txt"

with open(input_path, "r", encoding="utf-8") as f:
    sentences = f.readlines()

random.seed(42)  
random.shuffle(sentences)

val_size = 1000
test_size = 1000

val_sentences = sentences[:val_size]
test_sentences = sentences[val_size:val_size+test_size]
train_sentences = sentences[val_size+test_size:]

with open("train.txt", "w", encoding="utf-8") as f:
    f.writelines(train_sentences)

with open("val.txt", "w", encoding="utf-8") as f:
    f.writelines(val_sentences)

with open("test.txt", "w", encoding="utf-8") as f:
    f.writelines(test_sentences)

print(f"Train: {len(train_sentences)}, Val: {len(val_sentences)}, Test: {len(test_sentences)}")
