from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load TinyLlama model and tokenizer
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
)

def answer_query(question, index, chunks, top_k=3):
    # Retrieve top-k most relevant chunks
    docs = index.similarity_search(question, k=top_k)
    context = "\n".join([doc.page_content for doc in docs])

    # Construct prompt
    prompt = f"<|system|>\nYou are a helpful assistant.\n<|user|>\n{context}\n\nQuestion: {question}\n<|assistant|>\n"

    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id
        )

    # Decode response
    full_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = full_output[len(prompt):].strip()
    return response
