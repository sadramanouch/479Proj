# Takes in a csv with data on GitHub issues as input and outputs a specified pickle file with relevant text from the issue vectorized with BERT
# Script for vectorizing is separate because it takes a very long time to do
# usage: python3 csv-to-bert path/to/input.csv path/to/output.pkl
# TODO add code to drop entries that aren't in english because I saw some russian in the taiga-ui dataset

import sys
import os
import random
import re
import string

import nltk
nltk.download('punkt_tab')
import numpy as np
import pandas as pd

import torch
from transformers import BertTokenizer, BertModel

# nltk.download("stopwords")
# nltk.download("punkt")

IN_CSV = sys.argv[1]
OUT_PKL = sys.argv[2]

SEED = 42
random.seed(SEED)
os.environ["PYTHONHASHSEED"] = str(SEED)
np.random.seed(SEED)

text_columns = ["issue_title", "issue_body"]

df_raw = pd.read_csv(IN_CSV)
df = df_raw.copy()

# df = df.sample(n=11)

# df["content"] = df["content"].fillna("")

for col in text_columns:
    df[col] = df[col].astype(str)

# Create text column based on title, description, and content
df["text"] = df[text_columns].apply(lambda x: " | ".join(x), axis=1)

print(df)

docs = df["text"].values
# tokenized_docs = df["text_clean"].values

print(f"Original dataframe: {df_raw.shape}")
print(f"Pre-processed dataframe: {df.shape}")

print(df)

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

# stuff from this point is mostly ChatGPT generated based on the tutorial, appears to work but be skeptical - mz

# Load pre-trained BERT model and tokenizer

# I'm pretty sure the tokenizer does preprocessing - mz
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased')

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
bert_model.to(device)

def bert_vectorize(texts, tokenizer, model, device):
    """Generate BERT embeddings for a list of texts.

    Args:
        texts: List of strings (documents).
        tokenizer: BERT tokenizer.
        model: BERT model.
        device: Device (CPU/GPU).

    Returns:
        List of BERT embeddings.
    """
    features = []
    model.eval()
    
    i = 0
    for text in texts:
        if i % 100 == 0:
            print(i, "/", len(texts))
        i += 1
        # Tokenize and encode inputs
        encoded_inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128
        )
        encoded_inputs = {key: val.to(device) for key, val in encoded_inputs.items()}

        # Pass through BERT
        with torch.no_grad():
            outputs = model(**encoded_inputs)
        
        # Extract pooled output (sentence-level vector)
        pooled_output = outputs.pooler_output
        features.append(pooled_output.cpu().numpy())

    return np.vstack(features)

# Prepare documents
docs = df["text"].values

# Generate BERT embeddings
vectorized_docs = None
print("Generating BERT embeddings...")
vectorized_docs = bert_vectorize(docs, tokenizer, bert_model, device)

# create a bert_vector column for exporting
df["bert_vector"] = [vector for vector in vectorized_docs]
print(df.shape[0], vectorized_docs.shape[0])
print(df)

df.to_pickle(OUT_PKL)