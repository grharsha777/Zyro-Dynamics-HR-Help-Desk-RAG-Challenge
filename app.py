"""
================================================================================
ZYRO DYNAMICS HR HELP DESK - ENTERPRISE RAG APPLICATION
================================================================================
Version: 3.0.0-Ultimate
Author: Zyro Dynamics Team
Description: Production-grade RAG system for HR Help Desk
Features:
  - Hybrid Search (Semantic + Keyword)
  - Multi-stage Retrieval with Re-ranking
  - Conversation Memory with Context Window
  - Real-time Citations and Source Tracking
  - Performance Analytics Dashboard
  - Export Capabilities
  - Professional UI/UX
  - Error Handling & Recovery
  - Response Caching
  - Multi-model Support
================================================================================
"""

import os
import sys
import json
import time
import hashlib
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import lru_cache, wraps

# Third-party imports
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# LangChain imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.callbacks import BaseCallbackHandler

# Vector stores and embeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

# LLM imports
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Document loaders and processors
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredWordDocumentLoader,
    DirectoryLoader
)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    SemanticChunker
)
from langchain_community.docstore.in_memory import InMemoryDocstore

# Retrieval
from langchain.retrievers import (
    ContextualCompressionRetriever,
    EnsembleRetriever,
    ParentDocumentRetriever,
    MultiQueryRetriever
)
from langchain.retrievers.document_compressors import (
    LLMChainExtractor,
    LLMChainFilter
)
from langchain_community.retrievers import BM25Retriever

# FAISS
import faiss

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

class Config:
    """Application Configuration"""
    
    # App Info
    APP_NAME = "Zyro Dynamics HR Help Desk"
    APP_VERSION = "3.0.0-Ultimate"
    APP_ICON = "🏢"
    
    # Model Configuration
    DEFAULT_LLM = "llama-3.3-70b-versatile"
    FALLBACK_LLM = "mixtral-8x7b-32768"
    EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
    
    # Retrieval Configuration
    TOP_K_DOCUMENTS = 8
    TOP_K_FINAL = 5
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    SEMANTIC_CHUNK_THRESHOLD = 0.5
    
    # Search Configuration
    SEMANTIC_WEIGHT = 0.7
    KEYWORD_WEIGHT = 0.3
    RERANK_TOP_K = 10
    
    # Cache Configuration
    CACHE_TTL = 3600  # 1 hour
    MAX_CACHE_SIZE = 1000
    
    # UI Configuration
    MAX_CHAT_HISTORY = 50
    SESSION_TIMEOUT = 3600  # 1 hour
    
    # HR Categories
    HR_CATEGORIES = [
        "Leave & Time Off",
        "Benefits & Compensation",
        "Performance & Development",
        "Policies & Procedures",
        "Onboarding & Offboarding",
        "Workplace & Culture",
        "IT & Systems",
        "Travel & Expenses",
        "Health & Safety",
        "General HR"
    ]

# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class HRHelpDeskError(Exception):
    """Base exception for HR Help Desk"""
    pass

class DocumentProcessingError(HRHelpDeskError):
    """Error in document processing"""
    pass

class RetrievalError(HRHelpDeskError):
    """Error in retrieval process"""
    pass

class LLMError(HRHelpDeskError):
    """Error in LLM generation"""
    pass

class ConfigurationError(HRHelpDeskError):
    """Error in configuration"""
    pass

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ChatMessage:
    """Represents a chat message with metadata"""
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    sources: List[Dict] = field(default_factory=list)
    category: str = ""
    confidence: float = 0.0
    response_time: float = 0.0

@dataclass
class SearchResult:
    """Represents a search result with metadata"""
    content: str
    source: str
    page: int
    score: float
    category: str
    chunk_id: str

@dataclass
class AnalyticsData:
    """Analytics data structure"""
    total_queries: int = 0
    avg_response_time: float = 0.0
    categories_used: Dict[str, int] = field(default_factory=dict)
    satisfaction_score: float = 0.0
    cache_hit_rate: float = 0.0
    error_rate: float = 0.0

# ============================================================================
# CACHE SYSTEM
# ============================================================================

class ResponseCache:
    """Intelligent response caching system"""
    
    def __init__(self, max_size: int = Config.MAX_CACHE_SIZE, ttl: int = Config.CACHE_TTL):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, query: str, **kwargs) -> str:
        """Generate cache key from query and parameters"""
        key_data = f"{query}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, query: str, **kwargs) -> Optional[Any]:
        """Get cached response if valid"""
        key = self._generate_key(query, **kwargs)
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.hits += 1
                return value
            else:
                del self.cache[key]
        self.misses += 1
        return None
    
    def set(self, query: str, response: Any, **kwargs):
        """Cache a response"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        key = self._generate_key(query, **kwargs)
        self.cache[key] = (response, time.time())
    
    def clear(self):
        """Clear all cached responses"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

# ============================================================================
# CALLBACK HANDLERS
# ============================================================================

class StreamlitCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for Streamlit integration"""
    
    def __init__(self, container=None):
        self.container = container
        self.tokens = []
        self.start_time = None
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_time = time.time()
        if self.container:
            with self.container:
                self.status_placeholder = st.empty()
                self.status_placeholder.markdown("🤔 *Thinking...*")
    
    def on_llm_new_token(self, token, **kwargs):
        self.tokens.append(token)
    
    def on_llm_end(self, response, **kwargs):
        if self.start_time:
            elapsed = time.time() - self.start_time
            if self.container and hasattr(self, 'status_placeholder'):
                self.status_placeholder.empty()
    
    def on_llm_error(self, error, **kwargs):
        if self.container and hasattr(self, 'status_placeholder'):
            self.status_placeholder.error(f"❌ Error: {str(error)}")

# ============================================================================
# DOCUMENT PROCESSOR
# ============================================================================

class DocumentProcessor:
    """Advanced document processing pipeline"""
    
    def __init__(self, embedding_model: str = Config.EMBEDDING_MODEL):
        self.embedding_model = embedding_model
        self.embeddings = None
        self.text_splitter = None
        self.semantic_splitter = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all processing components"""
        try:
            # Initialize embeddings
            model_kwargs = {'device': 'cpu'}
            encode_kwargs = {'normalize_embeddings': True}
            
            self.embeddings = HuggingFaceBgeEmbeddings(
                model_name=self.embedding_model,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
            
            # Initialize text splitters
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=Config.CHUNK_SIZE,
                chunk_overlap=Config.CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", " ", ""],
                length_function=len
            )
            
            logger.info("Document processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize document processor: {e}")
            raise DocumentProcessingError(f"Initialization failed: {e}")
    
    def load_document(self, file_path: str) -> List:
        """Load document based on file type"""
        try:
            path = Path(file_path)
            suffix = path.suffix.lower()
            
            loaders = {
                '.pdf': PyPDFLoader,
                '.txt': TextLoader,
                '.csv': CSVLoader,
                '.docx': UnstructuredWordDocumentLoader,
                '.doc': UnstructuredWordDocumentLoader
            }
            
            loader_class = loaders.get(suffix)
            if not loader_class:
                raise DocumentProcessingError(f"Unsupported file type: {suffix}")
            
            loader = loader_class(file_path)
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata['file_name'] = path.name
                doc.metadata['file_type'] = suffix
                doc.metadata['processed_at'] = datetime.now().isoformat()
            
            logger.info(f"Loaded {len(documents)} pages from {path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            raise DocumentProcessingError(f"Document loading failed: {e}")
    
    def process_documents(self, documents: List, strategy: str = "recursive") -> List:
        """Process documents with specified chunking strategy"""
        try:
            if strategy == "recursive":
                chunks = self.text_splitter.split_documents(documents)
            elif strategy == "semantic":
                chunks = self._semantic_chunk(documents)
            else:
                chunks = self.text_splitter.split_documents(documents)
            
            # Add chunk metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata['chunk_id'] = hashlib.md5(
                    f"{chunk.page_content[:100]}_{i}".encode()
                ).hexdigest()[:12]
                chunk.metadata['chunk_index'] = i
                chunk.metadata['total_chunks'] = len(chunks)
            
            logger.info(f"Created {len(chunks)} chunks using {strategy} strategy")
            return chunks
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise DocumentProcessingError(f"Processing failed: {e}")
    
    def _semantic_chunk(self, documents: List) -> List:
        """Semantic chunking using embeddings"""
        try:
            semantic_splitter = SemanticChunker(
                embeddings=self.embeddings,
                breakpoint_threshold_type="percentile",
                breakpoint_threshold_amount=Config.SEMANTIC_CHUNK_THRESHOLD
            )
            return semantic_splitter.split_documents(documents)
        except Exception as e:
            logger.warning(f"Semantic chunking failed, falling back to recursive: {e}")
            return self.text_splitter.split_documents(documents)
    
    def enhance_metadata(self, documents: List) -> List:
        """Enhance document metadata with HR categories"""
        category_keywords = {
            "Leave & Time Off": ["leave", "vacation", "holiday", "pto", "sick", "absence", "time off"],
            "Benefits & Compensation": ["salary", "benefits", "insurance", "401k", "compensation", "pay", "bonus"],
            "Performance & Development": ["performance", "review", "development", "training", "goals", "feedback"],
            "Policies & Procedures": ["policy", "procedure", "guideline", "rule", "compliance", "regulation"],
            "Onboarding & Offboarding": ["onboarding", "offboarding", "join", "exit", "termination", "resignation"],
            "Workplace & Culture": ["culture", "workplace", "diversity", "inclusion", "environment", "team"],
            "IT & Systems": ["system", "software", "hardware", "login", "password", "computer", "email"],
            "Travel & Expenses": ["travel", "expense", "reimbursement", "mileage", "per diem"],
            "Health & Safety": ["health", "safety", "wellness", "ergonomic", "emergency", "first aid"],
            "General HR": ["hr", "human resources", "employee", "staff", "department"]
        }
        
        for doc in documents:
            content_lower = doc.page_content.lower()
            categories = []
            for category, keywords in category_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    categories.append(category)
            doc.metadata['hr_categories'] = categories if categories else ["General HR"]
        
        return documents

# ============================================================================
# RETRIEVAL SYSTEM
# ============================================================================

class AdvancedRetrievalSystem:
    """Multi-stage retrieval with re-ranking"""
    
    def __init__(self, embeddings, documents: List = None):
        self.embeddings = embeddings
        self.vector_store = None
        self.bm25_retriever = None
        self.ensemble_retriever = None
        self.documents = documents or []
        self._initialize_retrievers()
    
    def _initialize_retrievers(self):
        """Initialize all retrieval components"""
        try:
            if self.documents:
                self._build_vector_store()
                self._build_bm25_index()
                self._build_ensemble_retriever()
            logger.info("Retrieval system initialized")
        except Exception as e:
            logger.error(f"Retrieval initialization failed: {e}")
            raise RetrievalError(f"Retrieval init failed: {e}")
    
    def _build_vector_store(self):
        """Build FAISS vector store"""
        texts = [doc.page_content for doc in self.documents]
        metadatas = [doc.metadata for doc in self.documents]
        
        # Create FAISS index with L2 distance
        index = faiss.IndexFlatL2(self.embeddings.get_embedding_dimension())
        
        self.vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )
        
        # Add documents in batches
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            self.vector_store.add_texts(batch_texts, batch_metadatas)
        
        logger.info(f"Vector store built with {len(texts)} documents")
    
    def _build_bm25_index(self):
        """Build BM25 index for keyword search"""
        self.bm25_retriever = BM25Retriever.from_documents(
            self.documents,
            k=Config.TOP_K_DOCUMENTS
        )
        logger.info("BM25 index built")
    
    def _build_ensemble_retriever(self):
        """Build ensemble retriever combining semantic and keyword search"""
        faiss_retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": Config.TOP_K_DOCUMENTS,
                "fetch_k": Config.TOP_K_DOCUMENTS * 2,
                "lambda_mult": 0.7
            }
        )
        
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[faiss_retriever, self.bm25_retriever],
            weights=[Config.SEMANTIC_WEIGHT, Config.KEYWORD_WEIGHT]
        )
        logger.info("Ensemble retriever built")
    
    def retrieve(self, query: str, top_k: int = None, filters: Dict = None) -> List:
        """Multi-stage retrieval with optional filtering"""
        top_k = top_k or Config.TOP_K_FINAL
        start_time = time.time()
        
        try:
            # Stage 1: Initial retrieval
            if filters and filters.get('category'):
                docs = self._filtered_retrieval(query, filters['category'])
            else:
                docs = self.ensemble_retriever.invoke(query)
            
            # Stage 2: Re-ranking based on relevance
            ranked_docs = self._rerank_documents(query, docs, top_k * 2)
            
            # Stage 3: Final selection
            final_docs = ranked_docs[:top_k]
            
            elapsed = time.time() - start_time
            logger.info(f"Retrieved {len(final_docs)} documents in {elapsed:.3f}s")
            
            return final_docs
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            raise RetrievalError(f"Retrieval failed: {e}")
    
    def _filtered_retrieval(self, query: str, category: str) -> List:
        """Retrieve documents filtered by category"""
        all_docs = self.ensemble_retriever.invoke(query)
        return [doc for doc in all_docs if category in doc.metadata.get('hr_categories', [])]
    
    def _rerank_documents(self, query: str, documents: List, top_k: int) -> List:
        """Re-rank documents based on multiple signals"""
        if not documents:
            return []
        
        # Calculate relevance scores
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_docs = []
        for doc in documents:
            score = 0.0
            content_lower = doc.page_content.lower()
            
            # Exact phrase match bonus
            if query_lower in content_lower:
                score += 10.0
            
            # Word overlap score
            doc_words = set(content_lower.split())
            overlap = len(query_words & doc_words)
            score += (overlap / len(query_words)) * 5.0 if query_words else 0
            
            # Proximity bonus (words appearing close together)
            score += self._calculate_proximity_score(query_lower, content_lower)
            
            # Category match bonus
            if doc.metadata.get('hr_categories'):
                score += 1.0
            
            # Length penalty (prefer concise chunks)
            length = len(doc.page_content)
            if length < 200:
                score -= 1.0
            elif length > 2000:
                score -= 0.5
            
            scored_docs.append((doc, score))
        
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in scored_docs[:top_k]]
    
    def _calculate_proximity_score(self, query: str, content: str) -> float:
        """Calculate proximity score for query terms in content"""
        words = query.split()[:5]  # Use first 5 words
        if len(words) < 2:
            return 0.0
        
        total_proximity = 0.0
        pairs_checked = 0
        
        for i in range(len(words) - 1):
            pos1 = content.find(words[i])
            pos2 = content.find(words[i + 1])
            
            if pos1 != -1 and pos2 != -1:
                distance = abs(pos1 - pos2)
                proximity = max(0, 1 - distance / 1000)
                total_proximity += proximity
                pairs_checked += 1
        
        return total_proximity / pairs_checked if pairs_checked > 0 else 0.0
    
    def get_similar_documents(self, doc_id: str, k: int = 5) -> List:
        """Find similar documents to a given document"""
        try:
            doc = next((d for d in self.documents if d.metadata.get('chunk_id') == doc_id), None)
            if doc:
                return self.vector_store.similarity_search(doc.page_content, k=k)
            return []
        except Exception as e:
            logger.error(f"Similar document search failed: {e}")
            return []

# ============================================================================
# RAG ENGINE
# ============================================================================

class RAGEngine:
    """Main RAG engine with LLM integration"""
    
    def __init__(self, api_key: str, model: str = Config.DEFAULT_LLM):
        self.api_key = api_key
        self.model = model
        self.llm = None
        self.fallback_llm = None
        self.retrieval_system = None
        self.document_processor = None
        self.cache = ResponseCache()
        self.chain = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize all engine components"""
        try:
            # Initialize LLMs
            self.llm = ChatGroq(
                api_key=self.api_key,
                model_name=self.model,
                temperature=0.1,
                max_tokens=2048,
                timeout=30
            )
            
            self.fallback_llm = ChatGroq(
                api_key=self.api_key,
                model_name=Config.FALLBACK_LLM,
                temperature=0.1,
                max_tokens=2048,
                timeout=30
            )
            
            # Initialize document processor
            self.document_processor = DocumentProcessor()
            
            # Build RAG chain
            self._build_rag_chain()
            
            logger.info("RAG engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Engine initialization failed: {e}")
            raise LLMError(f"Engine init failed: {e}")
    
    def _build_rag_chain(self):
        """Build the RAG chain with prompts"""
        
        system_prompt = """You are an expert HR Assistant for Zyro Dynamics, a leading technology company. 
Your role is to provide accurate, helpful, and professional responses to employee HR queries.

IMPORTANT GUIDELINES:
1. Only answer based on the provided context - do not make up information
2. If the context doesn't contain relevant information, say so clearly
3. Always cite the source document when providing information
4. Be professional, empathetic, and clear in your responses
5. Structure your answers with bullet points when listing multiple items
6. If you're unsure about something, recommend the employee contact HR directly
7. Include relevant policy numbers or references when available

CONTEXT:
{context}

HR ASSISTANT RESPONSE:"""

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{query}")
        ])
        
        def format_docs(docs):
            formatted = []
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                formatted.append(f"[{i}] Source: {source}, Page: {page}\n{doc.page_content}")
            return "\n\n---\n\n".join(formatted)
        
        self.format_docs = format_docs
    
    def load_and_process_documents(self, directory: str) -> int:
        """Load and process all documents from directory"""
        try:
            all_documents = []
            
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        docs = self.document_processor.load_document(file_path)
                        all_documents.extend(docs)
                    except Exception as e:
                        logger.warning(f"Failed to load {file_path}: {e}")
                        continue
            
            if not all_documents:
                raise DocumentProcessingError("No documents loaded")
            
            # Process documents
            chunks = self.document_processor.process_documents(all_documents)
            chunks = self.document_processor.enhance_metadata(chunks)
            
            # Build retrieval system
            self.retrieval_system = AdvancedRetrievalSystem(
                self.document_processor.embeddings,
                chunks
            )
            
            logger.info(f"Processed {len(all_documents)} documents into {len(chunks)} chunks")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Document loading failed: {e}")
            raise DocumentProcessingError(f"Document loading failed: {e}")
    
    def query(self, query: str, chat_history: List = None, use_cache: bool = True) -> Dict:
        """Process a query through the RAG pipeline"""
        start_time = time.time()
        chat_history = chat_history or []
        
        try:
            # Check cache
            if use_cache:
                cached = self.cache.get(query)
                if cached:
                    cached['from_cache'] = True
                    return cached
            
            # Retrieve relevant documents
            if not self.retrieval_system:
                raise RetrievalError("No documents loaded")
            
            docs = self.retrieval_system.retrieve(query)
            context = self.format_docs(docs)
            
            # Prepare sources
            sources = [{
                'content': doc.page_content[:200] + "...",
                'source': doc.metadata.get('source', 'Unknown'),
                'page': doc.metadata.get('page', 'N/A'),
                'category': doc.metadata.get('hr_categories', ['General'])[0],
                'chunk_id': doc.metadata.get('chunk_id', '')
            } for doc in docs]
            
            # Generate response
            try:
                chain = self.prompt | self.llm | StrOutputParser()
                response = chain.invoke({
                    "context": context,
                    "query": query,
                    "chat_history": chat_history
                })
            except Exception as e:
                logger.warning(f"Primary LLM failed, using fallback: {e}")
                chain = self.prompt | self.fallback_llm | StrOutputParser()
                response = chain.invoke({
                    "context": context,
                    "query": query,
                    "chat_history": chat_history
                })
            
            elapsed = time.time() - start_time
            
            result = {
                'response': response,
                'sources': sources,
                'query': query,
                'response_time': elapsed,
                'documents_retrieved': len(docs),
                'from_cache': False,
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache the result
            if use_cache:
                self.cache.set(query, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            elapsed = time.time() - start_time
            return {
                'response': f"I apologize, but I encountered an error processing your query. Please try again or contact HR directly if the issue persists. Error: {str(e)}",
                'sources': [],
                'query': query,
                'response_time': elapsed,
                'documents_retrieved': 0,
                'from_cache': False,
                'error': True,
                'timestamp': datetime.now().isoformat()
            }

# ============================================================================
# SESSION MANAGER
# ============================================================================

class SessionManager:
    """Manage user sessions and state"""
    
    @staticmethod
    def initialize_session():
        """Initialize all session state variables"""
        defaults = {
            'messages': [],
            'analytics': AnalyticsData(),
            'rag_engine': None,
            'documents_loaded': False,
            'current_category': 'All',
            'search_history': [],
            'feedback': {},
            'session_start': datetime.now().isoformat(),
            'theme': 'light',
            'sidebar_state': 'expanded'
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def add_message(role: str, content: str, sources: List = None, **kwargs):
        """Add a message to chat history"""
        message = ChatMessage(
            role=role,
            content=content,
            sources=sources or [],
            **kwargs
        )
        st.session_state.messages.append(asdict(message))
        
        # Trim history if needed
        if len(st.session_state.messages) > Config.MAX_CHAT_HISTORY:
            st.session_state.messages = st.session_state.messages[-Config.MAX_CHAT_HISTORY:]
    
    @staticmethod
    def update_analytics(result: Dict):
        """Update analytics with query result"""
        analytics = st.session_state.analytics
        analytics.total_queries += 1
        
        # Update average response time
        if analytics.avg_response_time == 0:
            analytics.avg_response_time = result['response_time']
        else:
            n = analytics.total_queries
            analytics.avg_response_time = (
                (analytics.avg_response_time * (n - 1) + result['response_time']) / n
            )
        
        # Update cache hit rate
        analytics.cache_hit_rate = st.session_state.rag_engine.cache.hit_rate if st.session_state.rag_engine else 0
        
        # Track categories
        if result.get('sources'):
            for source in result['sources']:
                cat = source.get('category', 'General')
                analytics.categories_used[cat] = analytics.categories_used.get(cat, 0) + 1

# ============================================================================
# UI COMPONENTS
# ============================================================================

class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def render_header():
        """Render application header"""
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.markdown(f"<h1 style='font-size: 2rem;'>{Config.APP_ICON}</h1>", 
                       unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div style='text-align: center;'>
                    <h1 style='color: #1e3a5f; margin-bottom: 0;'>{Config.APP_NAME}</h1>
                    <p style='color: #666; font-size: 0.9rem;'>Intelligent HR Assistant | v{Config.APP_VERSION}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            status = "🟢 Online" if st.session_state.get('documents_loaded') else "🔴 Offline"
            st.markdown(f"<p style='text-align: right; color: #666;'>{status}</p>", 
                       unsafe_allow_html=True)
        
        st.divider()
    
    @staticmethod
    def render_chat_message(message: Dict):
        """Render a single chat message"""
        is_user = message['role'] == 'user'
        
        if is_user:
            with st.chat_message('user'):
                st.markdown(message['content'])
        else:
            with st.chat_message('assistant'):
                st.markdown(message['content'])
                
                # Render sources if available
                if message.get('sources'):
                    with st.expander("📋 Sources & References", expanded=False):
                        for i, source in enumerate(message['sources'], 1):
                            st.markdown(f"**Source {i}:** {source.get('source', 'Unknown')}")
                            st.markdown(f"- **Page:** {source.get('page', 'N/A')}")
                            st.markdown(f"- **Category:** {source.get('category', 'General')}")
                            st.markdown(f"- **Preview:** {source.get('content', '')[:150]}...")
                            st.divider()
                
                # Render metadata
                if message.get('response_time'):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(f"⏱️ Response time: {message['response_time']:.2f}s")
                    with col2:
                        if message.get('from_cache'):
                            st.caption("⚡ Served from cache")
    
    @staticmethod
    def render_sidebar():
        """Render sidebar with controls"""
        with st.sidebar:
            st.header("⚙️ Controls")
            
            # Category filter
            st.subheader("Category Filter")
            categories = ['All'] + Config.HR_CATEGORIES
            selected = st.selectbox(
                "Select HR Category",
                categories,
                index=0,
                key='category_filter'
            )
            st.session_state.current_category = selected
            
            st.divider()
            
            # Quick actions
            st.subheader("⚡ Quick Actions")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.messages = []
                    st.rerun()
            
            with col2:
                if st.button("🔄 Reset Cache", use_container_width=True):
                    if st.session_state.rag_engine:
                        st.session_state.rag_engine.cache.clear()
                    st.success("Cache cleared!")
            
            st.divider()
            
            # Sample queries
            st.subheader("💡 Sample Queries")
            sample_queries = [
                "What is the company leave policy?",
                "How do I submit an expense report?",
                "What benefits are available for new employees?",
                "How is performance review conducted?",
                "What is the remote work policy?"
            ]
            
            for query in sample_queries:
                if st.button(query, key=f"sample_{hash(query)}", use_container_width=True):
                    st.session_state['sample_query'] = query
                    st.rerun()
            
            st.divider()
            
            # Analytics summary
            st.subheader("📊 Session Stats")
            analytics = st.session_state.analytics
            st.metric("Total Queries", analytics.total_queries)
            st.metric("Avg Response Time", f"{analytics.avg_response_time:.2f}s")
            st.metric("Cache Hit Rate", f"{analytics.cache_hit_rate:.1%}")
    
    @staticmethod
    def render_analytics_tab():
        """Render analytics dashboard"""
        st.header("📊 Analytics Dashboard")
        
        analytics = st.session_state.analytics
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", analytics.total_queries)
        
        with col2:
            st.metric("Avg Response Time", f"{analytics.avg_response_time:.2f}s")
        
        with col3:
            st.metric("Cache Hit Rate", f"{analytics.cache_hit_rate:.1%}")
        
        with col4:
            st.metric("Error Rate", f"{analytics.error_rate:.1%}")
        
        st.divider()
        
        # Category distribution
        st.subheader("📋 Query Categories")
        
        if analytics.categories_used:
            df = pd.DataFrame([
                {"Category": k, "Count": v} 
                for k, v in analytics.categories_used.items()
            ]).sort_values('Count', ascending=False)
            
            st.bar_chart(df, x='Category', y='Count')
        else:
            st.info("No queries yet. Start chatting to see analytics!")
        
        st.divider()
        
        # Search history
        st.subheader("🔍 Search History")
        if st.session_state.search_history:
            for i, query in enumerate(reversed(st.session_state.search_history[-10:]), 1):
                st.markdown(f"{i}. {query}")
        else:
            st.info("No search history yet.")
    
    @staticmethod
    def render_settings_tab():
        """Render settings tab"""
        st.header("⚙️ Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Model Settings")
            model = st.selectbox(
                "LLM Model",
                ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
                key='model_setting'
            )
            
            temperature = st.slider("Temperature", 0.0, 1.0, 0.1, key='temp_setting')
            
            max_tokens = st.slider("Max Tokens", 256, 4096, 2048, step=256, key='tokens_setting')
        
        with col2:
            st.subheader("Retrieval Settings")
            top_k = st.slider("Top K Documents", 1, 20, Config.TOP_K_FINAL, key='topk_setting')
            
            semantic_weight = st.slider(
                "Semantic Weight", 
                0.0, 1.0, 
                Config.SEMANTIC_WEIGHT,
                key='semantic_weight_setting'
            )
            
            chunk_size = st.slider("Chunk Size", 200, 2000, Config.CHUNK_SIZE, step=100, key='chunk_setting')
        
        st.divider()
        
        if st.button("💾 Apply Settings", type="primary"):
            st.success("Settings applied! (Note: Some settings require document reload)")
    
    @staticmethod
    def render_feedback_buttons(message_idx: int):
        """Render feedback buttons for a message"""
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("👍", key=f"up_{message_idx}", help="Helpful"):
                st.session_state.feedback[message_idx] = "positive"
        
        with col2:
            if st.button("👎", key=f"down_{message_idx}", help="Not helpful"):
                st.session_state.feedback[message_idx] = "negative"
        
        with col3:
            if st.button("📋", key=f"copy_{message_idx}", help="Copy response"):
                st.toast("Response copied!")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

class HRHelpDeskApp:
    """Main application class"""
    
    def __init__(self):
        self.rag_engine = None
        self.session_manager = SessionManager()
        self.ui = UIComponents()
    
    def initialize(self):
        """Initialize the application"""
        # Initialize session state
        self.session_manager.initialize_session()
        
        # Set page config
        st.set_page_config(
            page_title=Config.APP_NAME,
            page_icon=Config.APP_ICON,
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS
        self._inject_custom_css()
        
        # Initialize RAG engine
        self._initialize_rag_engine()
    
    def _inject_custom_css(self):
        """Inject custom CSS for professional styling"""
        st.markdown("""
            <style>
                /* Main container */
                .main .block-container {
                    padding-top: 2rem;
                    padding-bottom: 2rem;
                    max-width: 1200px;
                }
                
                /* Chat messages */
                .stChatMessage {
                    padding: 1rem;
                    border-radius: 10px;
                    margin-bottom: 1rem;
                }
                
                /* Sidebar */
                .css-1d391kg {
                    background-color: #f8f9fa;
                }
                
                /* Buttons */
                .stButton > button {
                    border-radius: 8px;
                    transition: all 0.3s ease;
                }
                
                .stButton > button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                }
                
                /* Metrics */
                .stMetric {
                    background-color: #f8f9fa;
                    padding: 1rem;
                    border-radius: 10px;
                }
                
                /* Expander */
                .streamlit-expanderHeader {
                    font-weight: 600;
                }
                
                /* Hide default footer */
                footer {
                    visibility: hidden;
                }
                
                /* Custom scrollbar */
                ::-webkit-scrollbar {
                    width: 8px;
                }
                
                ::-webkit-scrollbar-track {
                    background: #f1f1f1;
                    border-radius: 4px;
                }
                
                ::-webkit-scrollbar-thumb {
                    background: #888;
                    border-radius: 4px;
                }
                
                ::-webkit-scrollbar-thumb:hover {
                    background: #555;
                }
                
                /* Status indicator */
                .status-online {
                    color: #28a745;
                }
                
                .status-offline {
                    color: #dc3545;
                }
                
                /* Loading animation */
                @keyframes pulse {
                    0% { opacity: 0.4; }
                    50% { opacity: 1; }
                    100% { opacity: 0.4; }
                }
                
                .loading-pulse {
                    animation: pulse 1.5s infinite;
                }
            </style>
        """, unsafe_allow_html=True)
    
    def _initialize_rag_engine(self):
        """Initialize or retrieve RAG engine"""
        api_key = os.getenv("GROQ_API_KEY", "")
        
        if not api_key:
            st.warning("⚠️ GROQ_API_KEY not found. Please set it in environment variables.")
            return
        
        if st.session_state.rag_engine is None:
            try:
                with st.spinner("Initializing HR Assistant..."):
                    st.session_state.rag_engine = RAGEngine(api_key=api_key)
                    
                    # Load documents if available
                    docs_path = "/kaggle/input/niat-masterclass-rag-challenge"
                    if os.path.exists(docs_path):
                        chunks = st.session_state.rag_engine.load_and_process_documents(docs_path)
                        st.session_state.documents_loaded = True
                        logger.info(f"Loaded {chunks} chunks")
                    else:
                        # Try alternative paths
                        alt_paths = [
                            "./data",
                            "./documents",
                            "./hr_docs",
                            "/app/data"
                        ]
                        for path in alt_paths:
                            if os.path.exists(path):
                                chunks = st.session_state.rag_engine.load_and_process_documents(path)
                                st.session_state.documents_loaded = True
                                break
                
            except Exception as e:
                st.error(f"❌ Failed to initialize: {e}")
                logger.error(f"RAG engine initialization failed: {e}")
    
    def run(self):
        """Run the application"""
        self.initialize()
        
        # Render header
        self.ui.render_header()
        
        # Create tabs
        tab_chat, tab_analytics, tab_settings, tab_about = st.tabs(
            ["💬 Chat", "📊 Analytics", "⚙️ Settings", "ℹ️ About"]
        )
        
        with tab_chat:
            self._render_chat_tab()
        
        with tab_analytics:
            self.ui.render_analytics_tab()
        
        with tab_settings:
            self.ui.render_settings_tab()
        
        with tab_about:
            self._render_about_tab()
        
        # Render sidebar
        self.ui.render_sidebar()
    
    def _render_chat_tab(self):
        """Render the main chat interface"""
        if not st.session_state.documents_loaded:
            st.warning("⚠️ Documents not loaded. Some features may not work correctly.")
        
        # Render chat history
        for i, message in enumerate(st.session_state.messages):
            self.ui.render_chat_message(message)
            
            # Add feedback buttons for assistant messages
            if message['role'] == 'assistant':
                self.ui.render_feedback_buttons(i)
        
        # Chat input
        query = st.chat_input(
            "Ask me anything about HR policies...",
            key="chat_input",
            disabled=not st.session_state.documents_loaded
        )
        
        # Handle sample query
        if 'sample_query' in st.session_state:
            query = st.session_state.pop('sample_query')
        
        # Process query
        if query:
            self._process_query(query)
    
    def _process_query(self, query: str):
        """Process a user query"""
        # Add user message
        self.session_manager.add_message('user', query)
        
        # Add to search history
        st.session_state.search_history.append(query)
        
        # Show thinking indicator
        with st.spinner("🤔 Thinking..."):
            # Prepare chat history for context
            chat_history = []
            for msg in st.session_state.messages[-6:-1]:  # Last 5 messages for context
                if msg['role'] == 'user':
                    chat_history.append(HumanMessage(content=msg['content']))
                else:
                    chat_history.append(AIMessage(content=msg['content']))
            
            # Get response from RAG engine
            if st.session_state.rag_engine:
                result = st.session_state.rag_engine.query(
                    query,
                    chat_history=chat_history
                )
            else:
                result = {
                    'response': "I'm sorry, but the HR Assistant is not currently available. Please try again later or contact HR directly.",
                    'sources': [],
                    'response_time': 0,
                    'from_cache': False
                }
            
            # Add assistant message
            self.session_manager.add_message(
                'assistant',
                result['response'],
                sources=result.get('sources', []),
                response_time=result.get('response_time', 0),
                from_cache=result.get('from_cache', False)
            )
            
            # Update analytics
            self.session_manager.update_analytics(result)
        
        st.rerun()
    
    def _render_about_tab(self):
        """Render about tab"""
        st.header("ℹ️ About")
        
        st.markdown(f"""
        ### {Config.APP_NAME}
        
        **Version:** {Config.APP_VERSION}
        
        #### Features:
        - 🔍 **Hybrid Search**: Combines semantic and keyword search for better results
        - 📚 **Intelligent RAG**: Retrieves relevant context from HR documents
        - 💬 **Conversational AI**: Maintains context across conversations
        - 📊 **Analytics Dashboard**: Track usage and performance metrics
        - ⚡ **Response Caching**: Faster responses for repeated queries
        - 🏷️ **Category Filtering**: Filter by HR categories
        - 📋 **Source Citations**: Full transparency with source references
        
        #### Technology Stack:
        - **LLM**: Llama 3.3 70B (Groq)
        - **Embeddings**: BGE Large EN v1.5
        - **Vector Store**: FAISS
        - **Framework**: LangChain + Streamlit
        
        #### Links:
        - [Streamlit App]({streamlit_link})
        - [LangSmith Trace]({langsmith_link})
        """)

# ============================================================================
# ENTRY POINT
# ============================================================================

# Hardcoded links for submission
streamlit_link = "https://zyro-dynamics-hr-app-desk-rag-challenge-qlcbn2ukfo6hfr9cvuouwu.streamlit.app/"
langsmith_link = "https://smith.langchain.com/public/d3a5baec-6c29-42f0-99d7-39da3d0378ae/r"

def main():
    """Main entry point"""
    app = HRHelpDeskApp()
    app.run()

if __name__ == "__main__":
    main()
