# chatbot.py
import os
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm
import google.generativeai as genai
import warnings

warnings.filterwarnings("ignore")  # Suppress minor warnings

# --- Configuration ---
KB_DIR = "kb_data"
CHUNKS_FILE = os.path.join(KB_DIR, "text_chunks.pkl")
EMBEDDINGS_FILE = os.path.join(KB_DIR, "embeddings.npy")
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'  # For retrieval
GEMINI_MODEL_NAME = 'gemini-2.0-flash'  # Or 'gemini-pro' - Flash is faster and often sufficient
MAX_CONTEXT_TOKENS = 500  # For context length estimation (approx)
TOP_K = 200  # Number of relevant chunks to retrieve

# --- Global Variables (Load models once) ---
embedding_model = None
gemini_model = None
text_chunks = None  # Holds the loaded text chunks
embeddings = None
models_loaded = False  # Flag to track loading status

# --- Helper Functions ---
def load_models_and_kb():
    """Loads embedding model, configures Gemini model, and loads knowledge base data."""
    global embedding_model, gemini_model, text_chunks, embeddings, models_loaded
    if models_loaded:  # Avoid reloading if already done
        print("Models and KB already loaded.")
        return True

    print("Loading models and knowledge base...")

    # Load Knowledge Base
    try:
        with open(CHUNKS_FILE, 'rb') as f:
            text_chunks = pickle.load(f)
        embeddings = np.load(EMBEDDINGS_FILE)
        if text_chunks is None or embeddings is None:
            raise ValueError("Loaded KB data is invalid.")
        print(f"Loaded {len(text_chunks)} chunks and embeddings.")
    except FileNotFoundError:
        print(f"Error: Knowledge base files not found in {KB_DIR}. Run knowledge_base.py first.")
        return False
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        return False

    # Load Embedding Model (for retrieval)
    try:
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")
    except Exception as e:
        print(f"Error loading SentenceTransformer model: {e}")
        return False

    # Configure Gemini Model (for generation)
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")

        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        print(f"Configured Gemini model: {GEMINI_MODEL_NAME}")
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please set the GOOGLE_API_KEY environment variable.")
        return False
    except Exception as e:
        print(f"Error configuring Gemini model: {e}")
        return False

    models_loaded = True  # Set flag after successful loading
    print("Models and knowledge base loaded successfully.")
    return True

def cosine_similarity(vec1, vec2):
    """Computes cosine similarity between two vectors."""
    vec1 = np.asarray(vec1)
    vec2 = np.asarray(vec2)
    norm1 = norm(vec1)
    norm2 = norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0  # Avoid division by zero
    return np.dot(vec1, vec2) / (norm1 * norm2)

def retrieve_relevant_chunks(query, top_k=TOP_K):
    """Retrieves the most relevant text chunks for a given query."""
    if not models_loaded or embedding_model is None or embeddings is None or text_chunks is None:
        print("Error: Models or KB not loaded properly.")
        return []

    try:
        query_embedding = embedding_model.encode([query], show_progress_bar=False)[0]

        # Calculate similarities
        similarities = np.array([cosine_similarity(query_embedding, emb) for emb in embeddings])

        # Get top_k indices
        num_chunks = len(similarities)
        actual_top_k = min(top_k, num_chunks)
        if actual_top_k <= 0:
            return []

        # Using partition is slightly more efficient than argsort for finding top k
        partitioned_indices = np.argpartition(similarities, -actual_top_k)[-actual_top_k:]
        # Sort only the top k indices by similarity score
        top_indices = partitioned_indices[np.argsort(similarities[partitioned_indices])[::-1]]

        # Add a similarity threshold
        similarity_threshold = 0.3
        relevant_chunks = [text_chunks[i] for i in top_indices if similarities[i] >= similarity_threshold]

        print(f"Retrieved {len(relevant_chunks)} relevant chunks (Top K={top_k}, Threshold={similarity_threshold}).")
        return relevant_chunks

    except Exception as e:
        print(f"Error during retrieval: {e}")
        return []

def generate_response(query, relevant_chunks):
    """Generates a response using the Gemini model based on query and context."""
    if not models_loaded or gemini_model is None:
        print("Error: Gemini model not loaded.")
        return "Sorry, I cannot generate a response right now (Model not ready)."

    if not relevant_chunks:
        return "Sorry, I couldn't find specific information related to your query in my current data."

    # Prepare context
    context = "\n".join([chunk['content'] for chunk in relevant_chunks])

    # Limit context size (Simple character limit)
    max_context_chars = 15000  # Increase limit for Gemini (adjust as needed)
    if len(context) > max_context_chars:
        original_len = len(context)
        context = context[:max_context_chars] + "..."
        print(f"Warning: Context truncated from {original_len} to {len(context)} chars for Gemini prompt.")

    # Create prompt for the Gemini model
    prompt = f"""You are a helpful assistant answering questions about restaurants based **ONLY** on the provided context information.

Context Information:
---
{context}
---

Based *solely* on the context above, answer the following question concisely and accurately.
If the answer cannot be found in the context, explicitly state that the information is not available in the provided data. Do not make up information or use external knowledge.
Answer very politely and attach few lines which support the statement.
Question: {query}

Answer:"""

    try:
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        response = gemini_model.generate_content(
            prompt,
            safety_settings=safety_settings,
            generation_config=genai.types.GenerationConfig(
                # Optional: Adjust temperature, top_p, top_k etc.
                # temperature=0.7
            )
        )

        # Handle potential safety blocks or empty responses
        if not response.parts:
            if response.prompt_feedback.block_reason:
                print(f"Warning: Gemini response blocked due to: {response.prompt_feedback.block_reason}")
                return f"Sorry, my response was blocked due to safety reasons ({response.prompt_feedback.block_reason}). Please rephrase your query."
            else:
                print("Warning: Gemini returned an empty response.")
                return "Sorry, I received an empty response. Please try again."

        generated_text = response.text.strip()
        print(f"Generated Response (Gemini): {generated_text}")
        return generated_text

    except Exception as e:
        print(f"Error during Gemini response generation: {e}")
        return "Sorry, I encountered an error while generating the response with the AI model."

# --- Main Function (for testing directly) ---
if __name__ == "__main__":
    # Ensure KB is created before running this directly
    kb_exists = os.path.exists(CHUNKS_FILE) and os.path.exists(EMBEDDINGS_FILE)
    if not kb_exists:
        print("Knowledge base files not found. Please run knowledge_base.py first.")
    elif load_models_and_kb():  # Load models if KB exists
        # Test queries
        test_queries = [
            "Which restaurant has Chicken Tikka?",
            "Tell me about vegetarian options at Awesome Restaurant 1",
            "What is the price range for desserts at Awesome Restaurant 2?",
            "Compare Awesome Restaurant 3 and Awesome Restaurant 4 features",
            "Does Awesome Restaurant 5 have wifi?",
            "What are the hours for Awesome Restaurant 6 on weekends?",
            "Tell me about gluten free food"
        ]

        for q in test_queries:
            print(f"\n--- Query: {q} ---")
            chunks = retrieve_relevant_chunks(q)
            answer = generate_response(q, chunks)
            print(f"Answer: {answer}")
            print("-" * 20)
    else:
        print("Failed to initialize chatbot components.")
