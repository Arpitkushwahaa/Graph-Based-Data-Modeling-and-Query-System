import os
from groq import Groq

# Use the GROQ API key from dotenv
client = Groq(api_key=os.environ.get("GROQ_API_KEY", "placeholder"))

def is_domain_relevant(question: str) -> bool:
    """ Guardrail to ensure query is related to the dataset """
    domain_keywords = ['order', 'delivery', 'invoice', 'payment', 'customer', 'product', 'cash', 'billing']
    q_lower = question.lower()
    return any(keyword in q_lower for keyword in domain_keywords)

def generate_natural_language_response(question: str, db_results="No specific data linked yet") -> str:
    if not is_domain_relevant(question):
        return "This system is designed to answer questions related to the provided Order-to-Cash dataset only."
    
    prompt = f"""
    You are a data assistant for an Order-to-Cash graph system.
    Answer the user's question clearly based on these underlying concepts (Orders, Deliveries, Invoices, Payments).
    
    User Question: {question}
    DB Results (simulated): {db_results}
    
    Format the answer concisely and directly. Do not generate code. Just explain the flow.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful data assistant focusing on Order-to-Cash processes.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return "Error connecting to LLM or generating response."
