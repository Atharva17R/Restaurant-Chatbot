# # knowledge_base.py
# import json
# import os
# import numpy as np
# from sentence_transformers import SentenceTransformer
# import pickle # To save processed data and embeddings

# # --- Configuration ---
# DATA_FILE = "restaurants.json"
# OUTPUT_DIR = "kb_data" # Directory to save knowledge base components
# EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2' # Efficient and effective model

# # --- Helper Functions ---
# def load_data(filepath):
#     """Loads restaurant data from JSON file."""
#     try:
#         with open(filepath, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         print(f"Loaded data for {len(data)} restaurants from {filepath}")
#         return data
#     except FileNotFoundError:
#         print(f"Error: Data file not found at {filepath}. Run scraper.py first.")
#         return None
#     except json.JSONDecodeError:
#         print(f"Error: Could not decode JSON from {filepath}.")
#         return None

# def create_text_chunks(restaurants_data):
#     """
#     Transforms restaurant data into text chunks suitable for embedding.
#     Each chunk should contain meaningful information and metadata (restaurant ID).
#     """
#     chunks = []
#     for restaurant in restaurants_data:
#         rest_id = restaurant.get("id", "unknown")
#         rest_name = restaurant.get("name", "N/A")

#         # Chunk 1: General Info
#         general_info = (
#             f"Restaurant Name: {rest_name}. "
#             f"Location: {restaurant.get('location', 'N/A')}. "
#             f"Cuisine: {restaurant.get('cuisine', 'N/A')}. "
#             f"Rating: {restaurant.get('rating', 'N/A')}. "
#             f"Features: {', '.join(restaurant.get('special_features', []))}. "
#             f"Hours: Mon-Fri {restaurant.get('operating_hours', {}).get('Mon-Fri', 'N/A')}, "
#             f"Sat-Sun {restaurant.get('operating_hours', {}).get('Sat-Sun', 'N/A')}. "
#             f"Contact: {restaurant.get('contact', {}).get('phone', 'N/A')}"
#         )
#         chunks.append({"restaurant_id": rest_id, "restaurant_name": rest_name, "content": general_info, "type": "general"})

#         # Chunk 2+: Menu Items
#         menu = restaurant.get("menu", {})
#         for category, items in menu.items():
#             for item in items:
#                 item_name = item.get('name', 'N/A')
#                 item_desc = item.get('description', '')
#                 item_price = item.get('price', 'N/A')
#                 item_tags = ", ".join(item.get('tags', []))
#                 menu_chunk = (
#                     f"Restaurant: {rest_name}. Menu Item: {item_name}. "
#                     f"Category: {category}. Description: {item_desc}. "
#                     f"Price: {item_price}. Tags: {item_tags}."
#                 )
#                 chunks.append({"restaurant_id": rest_id, "restaurant_name": rest_name, "content": menu_chunk, "type": "menu_item", "item_name": item_name})

#     print(f"Created {len(chunks)} text chunks from restaurant data.")
#     return chunks

# def generate_embeddings(text_chunks, model):
#     """Generates embeddings for the text chunks."""
#     contents = [chunk['content'] for chunk in text_chunks]
#     print(f"Generating embeddings for {len(contents)} chunks using '{EMBEDDING_MODEL_NAME}'...")
#     embeddings = model.encode(contents, show_progress_bar=True)
#     print("Embeddings generated successfully.")
#     return embeddings

# def save_knowledge_base(chunks, embeddings, output_dir):
#     """Saves the processed chunks and their embeddings."""
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#         print(f"Created directory: {output_dir}")

#     chunks_path = os.path.join(output_dir, "text_chunks.pkl")
#     embeddings_path = os.path.join(output_dir, "embeddings.npy")

#     try:
#         with open(chunks_path, 'wb') as f:
#             pickle.dump(chunks, f)
#         np.save(embeddings_path, embeddings)
#         print(f"Saved text chunks to {chunks_path}")
#         print(f"Saved embeddings to {embeddings_path}")
#     except IOError as e:
#         print(f"Error saving knowledge base files: {e}")
#     except pickle.PicklingError as e:
#          print(f"Error pickling text chunks: {e}")


# # --- Main Execution ---
# if __name__ == "__main__":
#     print("Starting knowledge base creation process...")

#     # 1. Load Data
#     restaurants = load_data(DATA_FILE)
#     if restaurants is None:
#         exit() # Stop if data loading failed

#     # 2. Create Text Chunks
#     text_chunks = create_text_chunks(restaurants)
#     if not text_chunks:
#         print("No text chunks were created. Exiting.")
#         exit()

#     # 3. Load Embedding Model
#     try:
#         embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
#         print(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")
#     except Exception as e:
#         print(f"Error loading SentenceTransformer model ('{EMBEDDING_MODEL_NAME}'): {e}")
#         print("Please ensure the model name is correct and you have an internet connection.")
#         exit()

#     # 4. Generate Embeddings
#     embeddings = generate_embeddings(text_chunks, embedding_model)

#     # 5. Save Knowledge Base
#     save_knowledge_base(text_chunks, embeddings, OUTPUT_DIR)

#     print("Knowledge base creation process finished.")

# knowledge_base.py
# knowledge_base.py
# import json
# import os
# import numpy as np
# from sentence_transformers import SentenceTransformer
# import pickle # To save processed data and embeddings

# # --- Configuration ---
# # Path: Look for the file in the current directory (as saved by the previous script)
# DATA_FILE = "restaurants.json"
# OUTPUT_DIR = "kb_data" # Directory to save knowledge base components
# EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2' # Efficient and effective model

# # --- Helper Functions ---
# def load_data(filepath):
#     """Loads the entire knowledge base data dictionary from JSON file."""
#     try:
#         with open(filepath, 'r', encoding='utf-8') as f:
#             # Load the entire dictionary structure from the JSON file
#             data = json.load(f)
#         print(f"Loaded data structure from {filepath}")
#         # This function now returns the full dictionary {'restaurants': {...}, 'indexes': {...}}
#         return data
#     except FileNotFoundError:
#         print(f"Error: Data file not found at {filepath}. Run the first script to create it.")
#         return None
#     except json.JSONDecodeError:
#         print(f"Error: Could not decode JSON from {filepath}. Please check the file content.")
#         return None
#     except Exception as e:
#         print(f"An unexpected error occurred while loading data: {e}")
#         return None


# def create_text_chunks(restaurants_data_dict):
#     """
#     Transforms the dictionary of restaurant data into text chunks suitable for embedding.
#     Each chunk should contain meaningful information and metadata (restaurant ID).
#     Expected input is the dictionary where keys are restaurant IDs (e.g., 'rest_0')
#     and values are the restaurant detail dictionaries.
#     """
#     chunks = []
#     # restaurants_data_dict is expected to be the dictionary like {'rest_0': {...}, 'rest_1': {...}}
#     if not isinstance(restaurants_data_dict, dict):
#         print("[WARNING] create_text_chunks received unexpected data format.")
#         return chunks # Return empty list if data format is wrong

#     for rest_id, restaurant in restaurants_data_dict.items(): # Iterate over the items (ID, restaurant_data)
#         # Ensure 'restaurant' is a dictionary before proceeding
#         if not isinstance(restaurant, dict):
#             print(f"[WARNING] Skipping invalid entry for ID {rest_id}.")
#             continue

#         rest_name = restaurant.get("name", "N/A")

#         # Skip restaurants with no name or potentially invalid data
#         if rest_name == "N/A": # We already checked for invalid dict above
#             print(f"[WARNING] Skipping entry {rest_id} due to missing name.")
#             continue

#         # --- Extracting data based on the structure from the previous script's JSON output ---
#         address_info = restaurant.get('address', {})
#         opening_info = restaurant.get('opening_info', {})
#         contact_info = restaurant.get('contact', {})
#         menu_info = restaurant.get('menu', []) # Menu was a list of item dicts
#         cuisine_info = restaurant.get('cuisine', []) # Cuisine was a list
#         price_range = restaurant.get('price_range', 'N/A')


#         # Format address nicely
#         full_address = address_info.get('full_address', 'N/A')

#         # Format opening hours
#         normalized_hours = opening_info.get('normalized', 'N/A')

#         # Get phone numbers (handled as a list in previous script)
#         phone_numbers = ", ".join([p for p in contact_info.get('phone', []) if p is not None and str(p).strip() != '' and str(p).strip() != 'nan']) if contact_info.get('phone') else 'N/A'


#         # Format cuisine
#         cuisines_str = ", ".join([c for c in cuisine_info if isinstance(c, str) and c.strip() != '']) if isinstance(cuisine_info, list) else 'N/A'


#         # --- Chunk 1: General Info ---
#         general_info = (
#             f"Restaurant Name: {rest_name}. "
#             f"Address: {full_address}. "
#             f"Cuisine types: {cuisines_str}. "
#             f"Price Range: {price_range}. "
#             f"Hours: {normalized_hours}. "
#             f"Contact Phone: {phone_numbers}. "
#             f"Current Status: {opening_info.get('status', 'unknown')}."
#             # Note: Rating, special_features are not in the source JSON structure
#         )
#         chunks.append({"restaurant_id": rest_id, "restaurant_name": rest_name, "content": general_info, "type": "general"})


#         # --- Chunk 2+: Menu Items ---
#         # The menu from the previous script is a list of item dictionaries, not a dict of categories.
#         if isinstance(menu_info, list) and menu_info: # Check if menu is a non-empty list
#             for item in menu_info:
#                  # Ensure item is a dictionary before accessing keys
#                  if not isinstance(item, dict):
#                       print(f"[WARNING] Skipping invalid menu item for restaurant {rest_id}.")
#                       continue

#                  item_name = item.get('name', 'N/A')
#                  item_price = item.get('price', 'N/A')
#                  item_category = item.get('category', 'N/A') # Category is available

#                  if item_name == 'N/A': continue # Skip if no item name

#                  # Format price nicely
#                  formatted_price = '₹' + str(item_price) if isinstance(item_price, (int, float)) else str(item_price)

#                  menu_chunk = (
#                      f"Restaurant: {rest_name}. Menu Item: {item_name}. "
#                      f"Category: {item_category}. "
#                      f"Price: {formatted_price}."
#                      # Tags and Description were not in the previous script's generated menu structure
#                  )
#                  chunks.append({"restaurant_id": rest_id, "restaurant_name": rest_name, "content": menu_chunk, "type": "menu_item", "item_name": item_name})
#         # If menu_info is not a list or is empty, no menu chunks are added, which is fine.


#     print(f"Created {len(chunks)} text chunks from restaurant data.")
#     return chunks

# def generate_embeddings(text_chunks, model):
#     """Generates embeddings for the text chunks."""
#     # Ensure text_chunks is not empty before trying to get content
#     if not text_chunks:
#         print("No chunks to embed.")
#         return np.array([]) # Return empty numpy array

#     contents = [chunk['content'] for chunk in text_chunks]
#     print(f"Generating embeddings for {len(contents)} chunks using '{EMBEDDING_MODEL_NAME}'...")
#     # Added a check for empty contents list
#     if not contents:
#         print("Contents list is empty, cannot generate embeddings.")
#         return np.array([])

#     try:
#         embeddings = model.encode(contents, show_progress_bar=True)
#         print("Embeddings generated successfully.")
#         return embeddings
#     except Exception as e:
#          print(f"Error during embedding generation: {e}")
#          return np.array([])


# def save_knowledge_base(chunks, embeddings, output_dir):
#     """Saves the processed chunks and their embeddings."""
#     # Ensure output directory exists
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#         print(f"Created directory: {output_dir}")

#     chunks_path = os.path.join(output_dir, "text_chunks.pkl")
#     embeddings_path = os.path.join(output_dir, "embeddings.npy")

#     try:
#         # Only save if chunks are not empty
#         if chunks:
#             with open(chunks_path, 'wb') as f:
#                 pickle.dump(chunks, f)
#             print(f"Saved text chunks to {chunks_path}")
#         else:
#             print("No chunks to save.")

#         # Only save embeddings if they are not empty
#         if embeddings.size > 0:
#             np.save(embeddings_path, embeddings)
#             print(f"Saved embeddings to {embeddings_path}")
#         else:
#             print("No embeddings to save.")

#     except IOError as e:
#         print(f"Error saving knowledge base files: {e}")
#     except pickle.PicklingError as e:
#         print(f"Error pickling text chunks: {e}")


# # --- Main Execution ---
# if __name__ == "__main__":
#     print("Starting knowledge base creation process...")

#     # 1. Load Data
#     # This will load the full dictionary {'restaurants': {...}, 'indexes': {...}}
#     full_kb_data = load_data(DATA_FILE)
#     if full_kb_data is None:
#         exit() # Stop if data loading failed

#     # 2. Extract the 'restaurants' dictionary from the loaded data
#     # This is the part that the create_text_chunks function expects
#     restaurants_data_dict = full_kb_data.get('restaurants')

#     # Check if the 'restaurants' key exists and is a dictionary
#     if not isinstance(restaurants_data_dict, dict) or not restaurants_data_dict:
#         print(f"Error: 'restaurants' key not found or is empty/invalid in {DATA_FILE}. Check the file content.")
#         exit()
#     else:
#         print(f"Extracted {len(restaurants_data_dict)} restaurant entries.")


#     # 3. Create Text Chunks - Pass the dictionary part
#     text_chunks = create_text_chunks(restaurants_data_dict)
#     if not text_chunks:
#         print("No text chunks were created. Exiting.")
#         exit()

#     # 4. Load Embedding Model
#     try:
#         embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
#         print(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")
#     except Exception as e:
#         print(f"Error loading SentenceTransformer model ('{EMBEDDING_MODEL_NAME}'): {e}")
#         print("Please ensure the model name is correct and you have an internet connection.")
#         print("You might need to install it: pip install sentence-transformers numpy") # numpy is usually installed with sentence-transformers, but good to mention
#         exit()

#     # 5. Generate Embeddings
#     embeddings = generate_embeddings(text_chunks, embedding_model)
#     # The generate_embeddings function now returns an empty array if there was an issue,
#     # so we check the size before saving.

#     # 6. Save Knowledge Base
#     # Only save if embeddings were successfully generated (size > 0)
#     if embeddings.size > 0:
#         save_knowledge_base(text_chunks, embeddings, OUTPUT_DIR)
#         print("Knowledge base creation process finished.")
#     elif text_chunks:
#          print("Embedding generation failed, knowledge base files were not saved.")
#     else:
#          print("No text chunks were created, knowledge base creation skipped.")

# knowledge_base.py
import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle # To save processed data and embeddings
import re # Import regex for basic text cleaning

# --- Configuration ---
# Path: Look for the file in the current directory
DATA_FILE = "restaurants.json"
OUTPUT_DIR = "kb_data" # Directory to save knowledge base components
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2' # Efficient and effective model

# --- Helper Functions ---
def load_data(filepath):
    """Loads the entire knowledge base data dictionary from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Load the entire dictionary structure from the JSON file
            data = json.load(f)
        print(f"Loaded data structure from {filepath}")
        # This function now returns the full dictionary {'restaurants': {...}, 'indexes': {...}}
        return data
    except FileNotFoundError:
        print(f"Error: Data file not found at {filepath}. Ensure 'restaurants.json' exists in the same directory.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}. Please check the file content for JSON syntax errors.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading data: {e}")
        return None

# Helper to format strings safely
def safe_str(item):
    return str(item) if item is not None else 'N/A'

# Helper to join list items safely
def safe_join(items, separator=", "):
    if not isinstance(items, list):
        return 'N/A'
    return separator.join([safe_str(item) for item in items if safe_str(item).strip() != '' and safe_str(item).strip() != 'N/A']).strip() or 'N/A'


def create_knowledge_base_chunks(full_data_dict):
    """
    Transforms the full data dictionary (including restaurants and indexes)
    into text chunks suitable for embedding.
    """
    chunks = []

    # Extract relevant parts from the full data dictionary
    restaurants_data_dict = full_data_dict.get('restaurants', {})
    indexes_data_dict = full_data_dict.get('indexes', {}) # Get the indexes data

    if not isinstance(restaurants_data_dict, dict):
        print("[WARNING] 'restaurants' key missing or not a dictionary.")
        restaurants_data_dict = {}

    if not isinstance(indexes_data_dict, dict):
        print("[WARNING] 'indexes' key missing or not a dictionary.")
        indexes_data_dict = {}

    print(f"Processing {len(restaurants_data_dict)} restaurant entries and {len(indexes_data_dict)} index entries.")


    # --- Process Restaurant Data ---
    for rest_id, restaurant in restaurants_data_dict.items():
        if not isinstance(restaurant, dict):
            print(f"[WARNING] Skipping invalid restaurant entry for ID {rest_id}.")
            continue

        rest_name = restaurant.get("name", "N/A")
        if rest_name == "N/A":
            print(f"[WARNING] Skipping restaurant entry {rest_id} due to missing name.")
            continue

        # Safely extract data using the helper functions
        address_info = restaurant.get('address', {})
        opening_info = restaurant.get('opening_info', {})
        contact_info = restaurant.get('contact', {})
        menu_info = restaurant.get('menu', []) # Menu is a list
        cuisine_info = restaurant.get('cuisine', []) # Cuisine is a list
        price_range = restaurant.get('price_range', 'N/A')
        # Add other potential keys if your JSON includes them, e.g., 'features', 'dietary_options', 'rating'

        full_address = safe_str(address_info.get('full_address'))
        normalized_hours = safe_str(opening_info.get('normalized'))
        phone_numbers = safe_join(contact_info.get('phone', []))
        cuisines_str = safe_join(cuisine_info)
        current_status = safe_str(opening_info.get('status', 'unknown'))
        price_range_str = safe_str(price_range)


        # --- Chunk 1: General Info ---
        general_info = (
            f"Restaurant Name: {rest_name}. "
            f"Cuisine types: {cuisines_str}. "
            f"Price Range: {price_range_str}. "
            f"Address: {full_address}. "
            f"Hours: {normalized_hours}. "
            f"Contact Phone: {phone_numbers}. "
            f"Current Status: {current_status}. "
            # Add other key features if available in your JSON
        )
        chunks.append({"restaurant_id": rest_id, "restaurant_name": rest_name, "content": general_info.strip(), "type": "general"})


        # --- Chunk 2+: Menu Items (Chunk per item) ---
        if isinstance(menu_info, list) and menu_info:
            for item in menu_info:
                if not isinstance(item, dict):
                    # print(f"[WARNING] Skipping invalid menu item for restaurant {rest_id}.") # Suppress frequent warnings
                    continue

                item_name = safe_str(item.get('name'))
                item_price = safe_str(item.get('price'))
                item_category = safe_str(item.get('category'))

                if item_name == 'N/A': continue

                # Format price nicely if it looks like a number
                try:
                    float_price = float(item_price)
                    formatted_price = f'₹{float_price:.2f}' # Assuming currency based on previous context
                except (ValueError, TypeError):
                    formatted_price = item_price # Use as is if not a number

                menu_chunk = (
                    f"Restaurant: {rest_name}. Menu Item: {item_name}. "
                    f"Category: {item_category}. "
                    f"Price: {formatted_price}."
                    # Add other menu item details if available (e.g., description, tags)
                )
                chunks.append({"restaurant_id": rest_id, "restaurant_name": rest_name, "content": menu_chunk.strip(), "type": "menu_item", "item_name": item_name})

        # If menu_info is not a list or is empty, no menu chunks are added, which is fine.


    # --- Process Index Data ---
    # Assuming the index data is a dictionary like {'rest_id': 'keywords/description text', ...}
    for rest_id, index_content in indexes_data_dict.items():
        # Find the restaurant name for this ID (lookup in the restaurants dict)
        restaurant = restaurants_data_dict.get(rest_id, {})
        rest_name = restaurant.get("name", f"Unknown Restaurant ({rest_id})") # Default name if not found

        if index_content and isinstance(index_content, str) and index_content.strip():
            index_chunk = f"Information for {rest_name} ({rest_id}): {index_content.strip()}"
            chunks.append({"restaurant_id": rest_id, "restaurant_name": rest_name, "content": index_chunk, "type": "index"})
        # If index_content is empty or not a string, it's skipped, which is fine.


    print(f"Created a total of {len(chunks)} text chunks.")
    return chunks

def generate_embeddings(text_chunks, model):
    """Generates embeddings for the text chunks."""
    if not text_chunks:
        print("No chunks to embed.")
        return np.array([])

    # Extract content strings, handling potential missing 'content' keys defensively
    contents = [chunk.get('content', '') for chunk in text_chunks if chunk and chunk.get('content', '').strip()]

    if not contents:
        print("No valid content strings found in chunks to embed.")
        return np.array([])

    print(f"Generating embeddings for {len(contents)} chunk contents using '{EMBEDDING_MODEL_NAME}'...")
    try:
        embeddings = model.encode(contents, show_progress_bar=True)
        print("Embeddings generated successfully.")
        # Optional: Add a check that the number of embeddings matches the number of contents
        if len(embeddings) != len(contents):
             print(f"[WARNING] Number of generated embeddings ({len(embeddings)}) does not match number of content strings ({len(contents)}).")
        return embeddings
    except Exception as e:
        print(f"Error during embedding generation: {e}")
        return np.array([])

# save_knowledge_base function remains the same
def save_knowledge_base(chunks, embeddings, output_dir):
    """Saves the processed chunks and their embeddings."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    chunks_path = os.path.join(output_dir, "text_chunks.pkl")
    embeddings_path = os.path.join(output_dir, "embeddings.npy")

    try:
        if chunks:
            with open(chunks_path, 'wb') as f:
                pickle.dump(chunks, f)
            print(f"Saved {len(chunks)} text chunks to {chunks_path}")
        else:
            print("No chunks to save.")

        if embeddings.size > 0:
            np.save(embeddings_path, embeddings)
            print(f"Saved {embeddings.shape[0]} embeddings to {embeddings_path}")
        else:
            print("No embeddings to save.")

    except IOError as e:
        print(f"Error saving knowledge base files: {e}")
    except pickle.PicklingError as e:
        print(f"Error pickling text chunks: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during saving: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    print("Starting knowledge base creation process...")

    # 1. Load Data (Loads the full dictionary including 'restaurants' and 'indexes')
    full_kb_data = load_data(DATA_FILE)
    if full_kb_data is None:
        print("Failed to load data. Exiting.")
        exit()

    # 2. Create Knowledge Base Chunks (Processes both 'restaurants' and 'indexes')
    # Pass the full loaded dictionary to the chunking function
    text_chunks = create_knowledge_base_chunks(full_kb_data)
    if not text_chunks:
        print("No text chunks were created. Exiting.")
        exit()

    # 3. Load Embedding Model
    try:
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")
    except Exception as e:
        print(f"Error loading SentenceTransformer model ('{EMBEDDING_MODEL_NAME}'): {e}")
        print("Please ensure the model name is correct and you have an internet connection.")
        print("You might need to install required libraries: pip install sentence-transformers numpy")
        exit()

    # 4. Generate Embeddings for ALL created chunks
    embeddings = generate_embeddings(text_chunks, embedding_model)
    # The generate_embeddings function returns an empty array if there was an issue

    # 5. Save Knowledge Base (Only save if embeddings were successfully generated)
    if embeddings.size > 0 and len(embeddings) == len(text_chunks):
         # Added check that number of embeddings matches number of chunks
         save_knowledge_base(text_chunks, embeddings, OUTPUT_DIR)
         print("Knowledge base creation process finished successfully.")
    elif embeddings.size == 0 and text_chunks:
         print("Embedding generation failed, knowledge base files were not saved.")
    else: # This might happen if text_chunks was empty initially (handled earlier) or size mismatch
         print("Knowledge base files were not saved due to errors in chunking or embedding generation.")