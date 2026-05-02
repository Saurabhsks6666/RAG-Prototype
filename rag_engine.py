import sqlite3
import os
from dotenv import load_dotenv

from deep_translator import GoogleTranslator
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

load_dotenv()

DB_PATH = "data/watrana.db"
CHROMA_DIR = "data/chroma_db"
PDF_FOLDER = "data/pdfs"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"
EMBEDDING_MODEL = "nomic-embed-text"

_qa_chains = {}


def normalize_language(language="english"):
    language = (language or "english").strip().lower()
    if language not in ["english", "hindi",]:
        language = "english"
    return language


def load_data_from_sqlite():
    """Loads all problems from SQLite database"""
    if not os.path.exists(DB_PATH):
        print(f"⚠️  Database not found at {DB_PATH}. Skipping SQLite load.")
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, year, category, problem, cause, solution, downtime_hours, department
        FROM problems
        ORDER BY year
    """)
    rows = cursor.fetchall()
    conn.close()

    documents = []
    for row in rows:
        id_, year, category, problem, cause, solution, downtime, department = row
        content = f"""
Source: Database
Problem ID: {id_}
Year: {year}
Category: {category}
Department: {department}
Downtime: {downtime} hours

PROBLEM:
{problem}

CAUSE / ROOT CAUSE:
{cause}

SOLUTION:
{solution}
        """.strip()

        metadata = {
            "source_type": "database",
            "id": id_,
            "year": year,
            "category": category,
            "department": department,
            "downtime_hours": downtime
        }
        documents.append(Document(page_content=content, metadata=metadata))

    print(f"✅ Loaded {len(documents)} problems from SQLite")
    return documents


def load_data_from_pdfs():
    """Loads all PDF files from data/pdfs/ folder"""
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER, exist_ok=True)
        print(f"📁 Created PDF folder: {PDF_FOLDER}")
        print("   Put your PDFs here and rebuild the index.")
        return []

    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"⚠️  No PDF files found in {PDF_FOLDER}. Skipping.")
        return []

    all_documents = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()

            for page in pages:
                page.metadata["source_type"] = "pdf"
                page.metadata["file_name"] = pdf_file
                page.metadata["page_number"] = page.metadata.get("page", 0) + 1

            all_documents.extend(pages)
            print(f"  ✅ {pdf_file} — {len(pages)} pages loaded")

        except Exception as e:
            print(f"  ❌ Failed to load {pdf_file}: {e}")

    print(f"✅ Loaded total {len(all_documents)} pages from PDFs ({len(pdf_files)} files)")
    return all_documents


def build_vector_store(force_rebuild=False):
    """Loads documents from SQLite + PDFs and builds/loads ChromaDB."""
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )

    if os.path.exists(CHROMA_DIR) and not force_rebuild:
        print("📂 Loading existing ChromaDB...")
        vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings
        )
        count = vectorstore._collection.count()
        print(f"✅ ChromaDB loaded — {count} vectors available")
        return vectorstore

    print("🔨 Building new ChromaDB...")

    db_documents = load_data_from_sqlite()
    pdf_documents = load_data_from_pdfs()
    all_documents = db_documents + pdf_documents

    if not all_documents:
        raise ValueError("❌ No documents found — neither in database nor PDFs!")

    print(f"\n📊 Total documents: {len(all_documents)}")
    print(f"   └─ Database: {len(db_documents)}")
    print(f"   └─ PDFs:     {len(pdf_documents)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    splits = text_splitter.split_documents(all_documents)
    print(f"\n✅ Created {len(splits)} text chunks")

    print("🔄 Generating embeddings...")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    print(f"✅ ChromaDB ready! {len(splits)} vectors saved.")
    return vectorstore


def get_language_rule(language):
    language = normalize_language(language)

    if language == "hindi":
        return """
IMPORTANT LANGUAGE RULE:
उत्तर केवल शुद्ध हिंदी और देवनागरी लिपि में दें।
English sentences का उपयोग न करें।
जरूरत पड़ने पर केवल technical words जैसे Motor, PLC, Sensor use कर सकते हैं।
"""

    if language == "hinglish":
        return """
IMPORTANT LANGUAGE RULE:
Answer strictly in Hinglish only.
Use Hindi words written in English letters.
Example: Motor overheating ka main reason cooling issue ho sakta hai.
Do not write Devanagari Hindi.
"""

    return """
IMPORTANT LANGUAGE RULE:
Answer strictly in English only.
Do not use Hindi or Hinglish words.
"""


def create_qa_chain(vectorstore, language="english"):
    """Creates Retrieval + LLM combination"""
    language = normalize_language(language)
    lang_rule = get_language_rule(language)

    prompt_template = f"""
You are an experienced technical expert at WATRANA company.
You have access to:
1. 20 years of problem-solution history from database
2. Technical documents and manuals from PDFs

Use the CONTEXT below to answer the user's question.

RULES:
{lang_rule}
- Use information from database records and PDF documents.
- Clearly mention useful source information in the answer.
- If relevant information is not in context, clearly say so.
- Give practical, actionable advice.
- For database records: mention year and category if available.
- For PDF sources: mention the document name if available.

CONTEXT:
{{context}}

QUESTION:
{{question}}

HELPFUL ANSWER:
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    llm = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        ),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    return qa_chain
def preprocess_user_query(user_query: str) -> dict:
    """
    User query ko validate aur clean karta hai.
    Small greetings/thanks ko LLM tak nahi bhejta.
    """

    query = user_query.strip()

    if not query:
        return {
            "allowed": False,
            "message": "Please enter a valid question.",
            "regulated_question": None
        }

    blocked_queries = [
        "hi", "hello", "hey", "hii", "hiii",
        "thanks", "thank you", "ok", "okay",
        "bye", "good morning", "good evening",
        "namaste", "namaskar"
    ]

    if query.lower() in blocked_queries:
        return {
            "allowed": False,
            "message": "Please ask a machine, maintenance, breakdown, quality, safety, or technical problem-related question.",
            "regulated_question": None
        }

    regulated_question = f"""
Find the most relevant solution for this industrial problem:

User problem:
{query}

Return answer using available database records and PDF manuals.
"""

    return {
        "allowed": True,
        "message": None,
        "regulated_question": regulated_question
    }


def get_qa_chain(language="english", force_rebuild=False):
    global _qa_chains

    language = normalize_language(language)

    if language not in _qa_chains or force_rebuild:
        print(f"🚀 Initializing RAG System for language: {language}")
        vectorstore = build_vector_store(force_rebuild)
        _qa_chains[language] = create_qa_chain(vectorstore, language)
        print("✅ RAG System ready!")

    return _qa_chains[language]


def ask_question(question: str, language="english") -> dict:
    preprocessed = preprocess_user_query(question)

    if not preprocessed["allowed"]:
        return {
            "answer": preprocessed["message"],
            "sources": [],
            "error": None
        }

    question = preprocessed["regulated_question"]
    """Take question and return answer with sources."""
    try:
        language = normalize_language(language)
        qa_chain = get_qa_chain(language)
        result = qa_chain.invoke({"query": question})

        sources = []
        seen = set()

        for doc in result.get("source_documents", []):
            meta = doc.metadata
            source_type = meta.get("source_type", "unknown")

            if source_type == "database":
                key = f"db_{meta.get('id')}"
            else:
                key = f"pdf_{meta.get('file_name')}_{meta.get('page_number')}"

            if key in seen:
                continue

            seen.add(key)

            if source_type == "database":
                sources.append({
                    "source_type": "database",
                    "id": meta.get("id"),
                    "year": meta.get("year"),
                    "category": meta.get("category"),
                    "department": meta.get("department"),
                    "downtime_hours": meta.get("downtime_hours"),
                    "preview": doc.page_content[:200] + "..."
                })
            else:
                sources.append({
                    "source_type": "pdf",
                    "file_name": meta.get("file_name"),
                    "page_number": meta.get("page_number"),
                    "preview": doc.page_content[:200] + "..."
                })
        
        return {
            "answer": result.get("result", ""),
            "sources": sources,
            "error": None
        }
    except Exception as e:
        return {
            "answer": "Kuch galat ho gaya. Please try again.",
            "sources": [],
            "error": str(e)
        }

    except Exception as e:
        error_msg = str(e)
    if "connection refused" in error_msg.lower() or "ollama" in error_msg.lower():
        error_msg = "Ollama server is not running. Run 'ollama serve' in terminal."
    return {
        "answer": None,
        "sources": [],
        "error": error_msg
    }


_translation_cache = {}

def translate_answer(answer: str, language="english") -> dict:
    """Translate already generated answer. No RAG retrieval happens here."""
    try:
        language = normalize_language(language)

        if language == "hindi":
            target = "hi"
        else:
            target = "en"
       

        translated_text = GoogleTranslator(
            source="auto",
            target=target
        ).translate(answer)

        return {
            "answer": translated_text,
            "error": None
        }

    except Exception as e:
        return {
            "answer": None,
            "error": str(e)
        }
        # cache_key = f"{language}:{answer.strip().lower()}"

        # # same translation already exists
        # if cache_key in _translation_cache:
        #     return _translation_cache[cache_key]

        # llm = ChatOllama(
        #     model=OLLAMA_MODEL,
        #     base_url=OLLAMA_BASE_URL,
        #     temperature=0
        # )

#         if language == "hindi":
#             instruction = """
# Translate the given answer into pure Hindi using Devanagari script only.
# Do not add new information.
# Do not change the meaning.
# English technical terms are allowed only when necessary.
# """
#         elif language == "hinglish":
#             instruction = """
# Translate the given answer into Hinglish.
# Use Hindi words written in English letters.
# Do not use Devanagari script.
# Do not add new information.
# Do not change the meaning.
# """
#         else:
#             instruction = """
# Translate the given answer into simple professional English only.
# Do not add new information.
# Do not change the meaning.
# """

#         prompt = f"""
# {instruction}

# ANSWER:
# {answer}

# TRANSLATED ANSWER:
# """

#         translated = llm.invoke(prompt)

#         response = {
#             "answer": translated.content,
#             "error": None
#         }

#         # save in cache
#         _translation_cache[cache_key] = response

#         return response

#     except Exception as e:
#         return {
#             "answer": None,
#             "error": str(e)
        
#         }

#     except Exception as e:
#         error_msg = str(e)
#         if "connection refused" in error_msg.lower() or "ollama" in error_msg.lower():
#             error_msg = "Ollama server is not running. Run 'ollama serve' in terminal."
#         return {
#             "answer": None,
#             "error": error_msg
#         }


def rebuild_index():
    """Creates fresh index from both Database and PDFs."""
    global _qa_chains
    _qa_chains = {}

    import shutil
    if os.path.exists(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR)
        print("🗑️  Deleted old ChromaDB")

    get_qa_chain("english", force_rebuild=True)
    return {"message": "Index successfully rebuilt from Database + PDFs!"}


if __name__ == "__main__":
    test_question = "What is the solution for motor overheating?"
    result = ask_question(test_question, "english")

    if result["error"]:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Answer:\n{result['answer']}")
        print(f"\n📚 Sources used: {len(result['sources'])}")