````markdown
# 🗺️ Stratum-MoE (Enterprise Customer Intelligence System)

**A high-performance agentic memory architecture with Mixture-of-Experts (MoE) routing.**  
Stratum-MoE combines **vector retrieval (pgvector)**, **semantic graph memory**, and **short/long-term memory** with **LangGraph orchestration** to answer strategic customer-support questions quickly—with **citations, confidence scores, and audit trails**.

---

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0%2B-green?style=flat)
![GPT-4o mini](https://img.shields.io/badge/GPT--4o--mini-OpenAI-412991?style=flat&logo=openai&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-336791?style=flat&logo=postgresql&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-0.5%2B-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat)

</div>

---

## Why Stratum-MoE

Customer success and support teams often spend hours manually scanning tickets, CRM notes, and tribal knowledge to answer questions like:

- “Why did enterprise customers churn in Q4?”
- “What compliance risks exist in our support conversations?”
- “Generate a health report for Acme Corp with evidence.”

**Stratum-MoE** solves this by routing each query through specialized experts (MoE), retrieving evidence from multiple memory planes, and producing **auditable answers**.

---

## Key Capabilities

### 🔀 LangGraph Orchestration
- Stateful workflow with typed state
- Conditional routing (MoE gating via LangGraph edges)
- Dynamic expert fan-out using `Send` (parallel execution)
- Checkpointing for multi-turn sessions
- Built-in visualization for debugging

### 🧠 Four-Plane Memory Architecture

| Plane | Purpose | Example |
|---|---|---|
| **STM** (Short-Term Memory) | Session context (TTL) | “User asked about pricing 2 mins ago” |
| **LTM** (Long-Term Memory) | Distilled patterns & trends | “Pricing complaints +40% in Q4” |
| **Semantic** | Structured facts w/ provenance | `acme → status → churned (0.95)` |
| **Vector** | Similarity search over raw artifacts | “Tickets similar to billing issues” |

### 🧾 Auditable Outputs
- Full citations back to tickets/facts/summaries
- Per-expert scores and final confidence score
- Gate rationale (why certain experts were/weren’t executed)
- Optional PII detection/redaction pass

---

## Architecture (High Level)

```text
                           STRATUM-MOE (LangGraph + MoE)
                           =============================

 USER QUERY
   │
   ▼
┌──────────────────┐       ┌───────────────────────────────────────────┐
│  LangGraph App   │       │         PostgreSQL + pgvector             │
│  (StateGraph)    │       │  ┌──────────────┐  ┌──────────────────┐  │
└───────┬──────────┘       │  │ Vector Store  │  │ Semantic Facts   │  │
        │                  │  │ (embeddings)  │  │ (graph-like)     │  │
        ▼                  │  └──────────────┘  └──────────────────┘  │
┌──────────────────┐       │  ┌──────────────┐  ┌──────────────────┐  │
│   MoE Gating     │       │  │ STM (TTL)     │  │ LTM (summaries)  │  │
│   (Router)       │       │  └──────────────┘  └──────────────────┘  │
└───┬─────┬─────┬──┘       └───────────────────────────────────────────┘
    │     │     │
    │  (parallel fan-out via Send)
    ▼     ▼     ▼
 Vector  Semantic  LTM/STM   Compliance
 Expert   Expert    Expert     Expert
    \       |         |         /
     \______|_________|________/
                │
                ▼
        Aggregation + Verification
                │
                ▼
        Synthesis (LLM) + Citations
                │
                ▼
     Writeback (optional learning loop)
````

---

## LangGraph Workflow

```python
graph = StateGraph(AgentState)

graph.add_node("load_preview", load_memory_preview)
graph.add_node("moe_gate", compute_gate_decision)
graph.add_node("run_experts", execute_experts_parallel)  # uses Send()
graph.add_node("aggregate", aggregate_expert_results)
graph.add_node("synthesize", generate_final_answer)
graph.add_node("writeback", update_memory_stores)
```

### Agent State (Typed)

```python
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    # input (immutable)
    query: str
    tenant_id: str
    session_id: str
    run_id: str

    # previews (loaded by load_preview)
    semantic_preview: dict
    vector_preview: dict
    stm_preview: dict
    ltm_preview: dict

    # gating decision (computed by moe_gate)
    gate_features: dict
    selected_experts: list[str]
    expert_weights: dict
    gate_rationale: str

    # expert results (accumulated)
    expert_results: Annotated[list, operator.add]

    # final outputs
    aggregated_data: dict
    final_answer: dict
```

---

## Explainable MoE Gating (Example)

```text
Query: "Why did Acme Corp churn?"

Gate Decision:
  ✓ SemanticQuery    (weight: 0.9) - 3 facts found
  ✓ LTMRecall        (weight: 0.8) - trend available
  ✗ VectorRetrieve   (skipped)     - semantic coverage sufficient
  ✓ Compliance       (weight: 1.0) - always run

Rationale: "High semantic confidence (0.92), skipping expensive vector search"
```

---

## Output Contract (Example)

```json
{
  "answer": "Acme Corp churned due to recurring pricing concerns mentioned across multiple tickets in Q4...",
  "confidence": 0.89,
  "citations": [
    {"type": "semantic", "fact_id": "f042", "source": "ticket_#1201"},
    {"type": "vector", "doc_id": "t_8831", "snippet": "billing dispute and renewal pricing..."},
    {"type": "ltm", "summary_id": "l005", "text": "Q4 pricing complaints up 40%"}
  ],
  "audit": {
    "gate_rationale": "High semantic coverage; skipped vector search",
    "experts_run": ["SemanticQuery", "LTMRecall", "Compliance"],
    "expert_scores": {"SemanticQuery": 0.92, "LTMRecall": 0.81, "Compliance": 1.0},
    "graph_execution_steps": 6,
    "pii_detected": false,
    "latency_ms": 847
  }
}
```

---

## Tech Stack

| Component                            | Technology                 |
| ------------------------------------ | -------------------------- |
| Runtime                              | Python 3.11+               |
| Package Manager                      | `uv`                       |
| Database                             | PostgreSQL 16+             |
| Vector Search                        | `pgvector`                 |
| ORM                                  | SQLAlchemy (Async)         |
| Orchestration                        | Docker Compose             |
| Agent Orchestration                  | LangGraph                  |
| LLM (Synthesis/Compliance/Writeback) | GPT-4o mini (configurable) |

---

## Project Structure

```text
moe-memorygraph/
├── src/moe_memorygraph/
│   ├── core/                 # config, types, errors, logging
│   ├── db/                   # SQLAlchemy models + repositories
│   ├── memory/               # STM/LTM/Semantic/Vector store interfaces
│   ├── experts/              # expert implementations
│   ├── gating/               # MoE routing logic (features + thresholds)
│   ├── graph/
│   │   ├── builder.py         # StateGraph construction
│   │   ├── state.py           # AgentState TypedDict
│   │   ├── nodes/
│   │   │   ├── load_preview.py
│   │   │   ├── gate_router.py
│   │   │   ├── run_experts.py
│   │   │   ├── aggregate.py
│   │   │   ├── synthesize.py
│   │   │   └── writeback.py
│   │   └── visualize.py       # graph rendering
│   ├── ingestion/            # HuggingFace → DB pipeline
│   └── cli/                  # CLI entrypoints
├── migrations/               # Alembic migrations
├── tests/                    # unit + integration tests
├── docs/                     # design docs
├── docker-compose.yml        # local Postgres + pgvector
└── pyproject.toml
```

---

## Dataset

Primary dataset for demos/testing:

* **Bitext Customer Support Dataset** (27k+ support conversations; intent labels):
  [https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset)

Supplementary:

* ai4privacy/pii-masking-300k (PII stress tests): [https://huggingface.co/datasets/ai4privacy/pii-masking-300k](https://huggingface.co/datasets/ai4privacy/pii-masking-300k)
* tau/soda (multi-turn conversations): [https://huggingface.co/datasets/tau/soda](https://huggingface.co/datasets/tau/soda)

---

## Quick Start

### Prerequisites

* Python 3.11+
* Docker + Docker Compose
* `uv` installed (recommended)

### 1) Start Postgres + pgvector

```bash
docker compose up -d
# or: docker-compose up -d
```

### 2) Install dependencies

```bash
uv sync
```

### 3) Configure environment

Create a `.env` (or copy from `.env.example` if you add one):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/memorygraph

# LLM (synthesis / compliance / writeback)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.1

# Embeddings (choose one approach)
# Option A: OpenAI embeddings
EMBED_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Option B: local sentence-transformers
# EMBED_PROVIDER=sentence-transformers
# EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# MoE Settings
MAX_CONCURRENT_EXPERTS=10
EXPERT_TIMEOUT_SEC=5
GATE_SEMANTIC_THRESHOLD=0.85

# LangGraph
LANGGRAPH_CHECKPOINTING=true
LANGGRAPH_DEBUG=false
LANGGRAPH_TRACE_DIR=./traces
```

### 4) Run migrations

```bash
uv run alembic upgrade head
```

### 5) Ingest sample data (Phase 3)

```bash
uv run python -m moe_memorygraph.cli.ingest --dataset bitext --limit 1000
```

### 6) Run a query

```bash
uv run python -m moe_memorygraph.cli.run_item \
  "Why did Acme Corp churn?" \
  --tenant acme_corp
```

### 7) Batch mode (compile once, run many)

```bash
uv run python -m moe_memorygraph.cli.run_batch queries.json
```

### 8) Visualize the graph

```bash
uv run python -m moe_memorygraph.graph.visualize --output graph.png
```

---

## Production-Grade Concurrency

* Parallel fan-out via LangGraph `Send`
* Semaphore-limited concurrency for backpressure
* Per-expert timeouts with graceful fallbacks
* Result accumulation with `Annotated[list, operator.add]`

---

## Testing

```bash
# run all tests
uv run pytest

# integration tests
uv run pytest tests/integration/test_graph_flow.py

# unit tests
uv run pytest tests/unit/test_gate_node.py
```

Recommended coverage:

* state transitions across nodes
* conditional edge routing (gating decisions)
* expert fan-out + accumulation correctness
* PII redaction rules
* tenant isolation (`tenant_id` enforced in all DB queries)

---

## Benchmarks (Reference)

Typical targets on a laptop-class machine:

* Graph compilation: ~150ms (one-time)
* Single query end-to-end: ~850ms (depends on I/O + LLM latency)
* Batch: 50 queries in ~30s (compile once; parallel experts)

> Treat these as indicative; real performance depends on model/provider, network, and DB tuning.

---

## Deployment

### Docker (single container)

```bash
docker build -t moe-memorygraph .
docker run --env-file .env moe-memorygraph
```

### LangGraph Cloud (managed execution)

```bash
langgraph deploy --graph moe_memorygraph.graph:app
```

### Kubernetes / Helm (optional)

```bash
helm install moe-memorygraph ./infra/k8s/helm/
```

---

## Roadmap

### Phase 1: Infrastructure (Done)

* Dockerized Postgres + pgvector
* `uv` environment
* centralized config

### Phase 2: Database Architecture (Done)

* SQLAlchemy models for VectorMemory + SemanticFact
* async session management
* DB init + migrations

### Phase 3: Knowledge Ingestion (Current)

* embedder utility
* Bitext loader → `vector_memories`
* verification queries + sanity checks

### Phase 4: Retrieval Engine

* VectorRetrieve expert
* hybrid retrieval (vector + keyword/BM25)
* accuracy tests + goldens

### Phase 5: Agentic Brain (MoE Finale)

* gating network/features + thresholds
* robust writeback loops (STM→LTM summarization)
* API surface (CLI + REST) + observability

---

## Security & Enterprise Controls

* **Multi-tenant isolation**: strict `tenant_id` in all queries + state
* **PII detection**: Compliance expert in the default route
* **Audit trails**: structured logs + trace export
* **Writeback governance**: enable/disable writeback by environment for safety

---

## Contributing

PRs welcome. Suggested areas:

* expert implementations (new domains, compliance policies)
* gating features and evaluation harness
* hybrid retrieval and re-ranking
* tracing / observability integrations
* performance profiling & DB indexing guides

---

## License

MIT License. See `LICENSE`.

---

## Contact

**Author:** Md Rezanur Islam
**Email:** [arupreza@sch.ac.kr](mailto:your.email@example.com)
**GitHub:** [https://github.com/Arupreza](https://github.com/yourusername)
**LinkedIn:** [https://linkedin.com/in/Arupreza](https://linkedin.com/in/yourprofile)

```
``