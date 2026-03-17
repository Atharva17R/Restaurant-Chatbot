# NuggetAssignment

# 🍽️ Zomato Restaurant Chatbot

A Streamlit-powered chatbot that uses Retrieval Augmented Generation (RAG) to answer questions about restaurants based on scraped Zomato data.

## 📝 Overview

This project creates an interactive chatbot that can answer questions about restaurants, menus, cuisines, and more. It uses a RAG (Retrieval Augmented Generation) approach, combining:

1. **Data Collection**: Scraping restaurant data from Zomato
2. **Knowledge Base**: Processing and indexing the data
3. **Retrieval**: Finding relevant information using semantic search
4. **Generation**: Providing natural language responses using Google's Gemini model

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+ installed
- Google API key for Gemini (see [Google AI Studio](https://ai.google.dev/))

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/zomato-restaurant-chatbot.git
cd zomato-restaurant-chatbot
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variable for Google API**

```bash
# On Linux/Mac
export GOOGLE_API_KEY="your_google_api_key_here"

# On Windows (Command Prompt)
set GOOGLE_API_KEY=your_google_api_key_here

# On Windows (PowerShell)
$env:GOOGLE_API_KEY="your_google_api_key_here"
```

### Data Preparation

1. **Run the scraper and build the knowledge base**

```bash
python scraper.py
```

This will:
- Scrape restaurant data from Zomato
- Save raw data to `Restaurants.csv`
- Process and create a knowledge base in `restaurants.json`

2. **Generate embeddings for the knowledge base**

```bash
python knowledge_base.py
```

This creates:
- `kb_data/text_chunks.pkl`: Processed text chunks for retrieval
- `kb_data/embeddings.npy`: Vector embeddings for semantic search

### Running the Application

```bash
streamlit run app.py
```

The chatbot interface will be available at `http://localhost:8501`

## 🤖 Using the Chatbot

- Ask questions about restaurants, their menus, cuisines, or locations
- Example queries:
  - "Which restaurants serve biryani?"
  - "What vegetarian options are available?"
  - "Tell me about restaurants in Roorkee"
  - "What is the price range of desserts?"
  - "Are there any restaurants open today?"

## 📁 Project Structure

- `scraper.py`: Scrapes restaurant data and builds initial knowledge base
- `knowledge_base.py`: Processes data and generates embeddings
- `chatbot.py`: Core RAG components for retrieval and generation
- `app.py`: Streamlit interface for user interaction
- `kb_data/`: Directory containing processed knowledge base files
- `restaurants.json`: Structured restaurant data
- `Restaurants.csv`: Raw scraped data

## ⚙️ Technical Details

- **Embedding Model**: `all-MiniLM-L6-v2` from Sentence Transformers
- **Generation Model**: Google's Gemini 2.0 Flash
- **UI Framework**: Streamlit
- **Search Algorithm**: Cosine similarity with semantic embeddings

## 📋 Notes

- The system uses simulated restaurant data created from scraped Zomato information
- The chatbot only answers based on information present in the knowledge base
- Performance depends on the quality and quantity of the scraped data

## 🔄 Workflow

1. User asks a question through the Streamlit interface
2. The system retrieves relevant chunks of information from the knowledge base
3. The retrieved context is passed to the Gemini model along with the query
4. The model generates a natural language response based on the context
5. The response is displayed in the chat interface

![Untitled diagram-2025-04-25-045544](https://github.com/user-attachments/assets/dff26941-53da-4360-9edc-dc4bfc9390e1)


"# Restaurant-Chatbot" 
