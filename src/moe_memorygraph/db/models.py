import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import String, DateTime, func, JSON, Float, Text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector

# 1. Base Class for all models
class Base(DeclarativeBase):
    pass

# 2. Vector Plane (Unstructured Data)
class VectorMemory(Base):
    """
    Stores unstructured data (tickets, chats) as embeddings for similarity search.
    """
    __tablename__ = "vector_memory"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    # Enterprise Multi-tenancy Isolation (According to the company name data grouped)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # The raw text content (e.g., "Customer complained about billing...")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata for filtering (e.g., {"source": "email", "date": "2024-01-01"})
    metadata_: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default={})
    
    # The Embedding Vector (384 dimensions is standard for all-MiniLM-L6-v2)
    # If you use OpenAI embeddings, change 384 to 1536.
    embedding: Mapped[List[float]] = mapped_column(Vector(384))
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # --- Database 'Search Engine' Configuration ---
    # Optimized for Cosine Similarity (Comparing the ANGLE between ideas)
    __table_args__ = (
        Index(
            "ix_vector_memory_embedding", 
            "embedding", 
            
            # HNSW: The algorithm that creates a 'web' of connections for fast travel
            postgresql_using="hnsw", 
            
            # Tuning the Web:
            # m: Each memory links to 16 'neighbors' (the size of the web)
            # ef_construction: 64 search points to find the best neighbors for accuracy
            postgresql_with={"m": 16, "ef_construction": 64}, 
            
            # The measuring tool: CHANGED to 'vector_cosine_ops'
            # This looks at how similar the "direction" of two ideas are.
            postgresql_ops={"embedding": "vector_cosine_ops"}, 
        ),
    )

# 3. Semantic Plane (Structured Facts)
class SemanticFact(Base):
    """
    Stores exact facts extracted from conversations.
    Example: Entity='Acme Corp', Attribute='Status', Value='Churned'
    """
    __tablename__ = "semantic_facts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # The Subject-Predicate-Object triple structure
    entity_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    attribute: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Confidence score from the extraction model (0.0 to 1.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Where did this fact come from? (Audit trail)
    source_id: Mapped[str] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

# 4. Long-Term Memory (LTM) Plane - Optional but recommended
class LTMPattern(Base):
    """
    Stores distilled patterns or summaries over time.
    """
    __tablename__ = "ltm_patterns"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    pattern_description: Mapped[str] = mapped_column(Text, nullable=False)
    frequency: Mapped[int] = mapped_column(default=1)
    last_observed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )