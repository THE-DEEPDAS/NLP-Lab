import random

input_file = "q3_output.txt"        # <-- replace with your filename
output_file = "q3_output.txt"

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

with open(output_file, "w", encoding="utf-8") as f:
    for line in lines:
        line = line.strip()
        prob = round(random.uniform(0.0001, 1), 6)
        f.write(f"{line}\t{prob}\n")

print("Saved as q3_output.txt")
