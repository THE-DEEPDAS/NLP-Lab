import pandas as pd

# Read each line as a sentence
with open("gu_sentences_indic_corp.txt", "r", encoding="utf-8", errors="ignore") as f:
    sentences = [line.strip() for line in f if line.strip()]  

# Create DataFrame
df = pd.DataFrame(sentences, columns=["text"])

# Save as Parquet
df.to_parquet("gu_sentences_indic_corp.parquet", index=False)