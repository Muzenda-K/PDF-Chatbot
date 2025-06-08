#!/usr/bin/env python
# coding: utf-8

# In[1]:


import PyPDF2

def extract_text(file_stream):
    reader = PyPDF2.PdfReader(file_stream)
    return "\n".join(page.extract_text() for page in reader.pages)

def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i+chunk_size])
    return chunks

