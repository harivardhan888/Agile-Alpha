import os
import requests
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

class SimpleHFEmbeddings(Embeddings):
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_name}"
        self.headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN', '')}"}

    def embed_documents(self, texts):
        try:
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json={"inputs": texts, "options": {"wait_for_model": True}}
            )
            result = response.json()
            # The API returns a list of embeddings. Sometimes they are nested if the model is not a formal sentence transformer.
            # We ensure we return a list of lists of floats.
            if isinstance(result, dict) and "error" in result:
                print(f"HF API Error: {result['error']}")
                return [[0.0] * 384 for _ in texts] # Fallback to zero vector
            
            # If the result is a 3D list (batch, seq, dim), we take the mean or first token (CLS)
            if len(result) > 0 and isinstance(result[0], list) and isinstance(result[0][0], list):
                return [embedding[0] for embedding in result] # Take first token (CLS)
            
            return result
        except Exception as e:
            print(f"Embedding error: {e}")
            return [[0.0] * 384 for _ in texts]

    def embed_query(self, text):
        return self.embed_documents([text])[0]

class RAGPipeline:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.persist_directory = "db"
        self.embeddings = SimpleHFEmbeddings()
        self.vector_store = None
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Initializes or loads the vector store."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            # Create a dummy file if empty to avoid errors
            with open(os.path.join(self.data_dir, "placeholder.txt"), "w") as f:
                f.write("Placeholder for financial documents.")

        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            print("Loading existing vector store...")
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            print("Creating new vector store...")
            from langchain_community.document_loaders import TextLoader
            
            documents = []
            for file in os.listdir(self.data_dir):
                file_path = os.path.join(self.data_dir, file)
                if file.endswith(".txt"):
                    from langchain_community.document_loaders import TextLoader
                    loader = TextLoader(file_path)
                    documents.extend(loader.load())
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(documents)
            
            self.vector_store = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )

    @tool("search_financial_reports")
    def search_financial_reports(query: str) -> str:
        """Searches through financial reports, SEC filings, and earnings transcripts for specific information."""
        global rag_instance
        try:
            results = rag_instance.vector_store.similarity_search(query, k=4)
            return "\n\n".join([doc.page_content for doc in results])
        except Exception as e:
            print(f"RAG Search failed: {e}. Falling back to simple keyword search.")
            # Simple fallback search
            content = ""
            for file in os.listdir(rag_instance.data_dir):
                if file.endswith(".txt"):
                    with open(os.path.join(rag_instance.data_dir, file), "r", encoding="utf-8") as f:
                        text = f.read()
                        if query.lower() in text.lower():
                            content += text[:1000] + "\n\n"
            return content if content else "No direct matches found in local reports."

# Global instance for tool access
rag_instance = RAGPipeline()
