import csv
import regex
from tokenizers import Tokenizer

with open(r"C:\IGRIS\TOKENIZER_HUMAN_REVIEW_SAMPLE.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Let's count words using text.split() vs regex word tokens \w+
total_whitespace_words = 0
total_regex_words = 0

for r in rows:
    text = r["original_text"]
    ws_words = text.split()
    total_whitespace_words += len(ws_words)
    rgx_words = regex.findall(r"\b\w+\b", text)
    total_regex_words += len(rgx_words)

print(f"Total whitespace-separated words: {total_whitespace_words}")
print(f"Total regex \\w+ words: {total_regex_words}")
