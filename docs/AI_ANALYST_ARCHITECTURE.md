# OlistIQ AI Analyst & LangGraph Architecture

## 1. System Overview

The **OlistIQ AI Analyst (Phase 6)** enables business users, executives, and analytics teams to query the entire e-commerce decision intelligence platform using natural language. Grounded in the analytical data warehouse (`data/processed/olistiq.db`) and integrated with Phase 5 machine learning inference engines, the system translates conversational questions into validated SQL or predictive ML routes.

```
                         ┌────────────────────────────────────┐
                         │       User Business Question       │
                         └─────────────────┬──────────────────┘
                                           │
                                           ▼
                         ┌────────────────────────────────────┐
                         │   Security Guardrails Inspection   │
                         │ (Prompt Injection / Attack Reject) │
                         └─────────────────┬──────────────────┘
                                           │
                                           ▼
                         ┌────────────────────────────────────┐
                         │      Intent Classification         │
                         │  (SQL Analytics vs ML Predictive)  │
                         └─────────┬────────────────┬─────────┘
                                   │                │
            [SQL Analytics Route]  │                │  [Predictive ML Route]
                                   ▼                ▼
     ┌───────────────────────────────┐    ┌───────────────────────────┐
     │  Schema & Metric Retrieval    │    │ Hybrid ML Router          │
     │  - schema_store.py            │    │ - Customer Segmentation   │
     │  - metric_catalog.py          │    │ - Delivery Delay Risk     │
     └──────────────┬────────────────┘    │ - GMV/Order Forecasting   │
                    │                     │ - Business Anomalies      │
                    ▼                     └─────────────┬─────────────┘
     ┌───────────────────────────────┐                  │
     │  Structured Query Planning    │                  │
     │  - query_planner.py           │                  │
     └──────────────┬────────────────┘                  │
                    │                                   │
                    ▼                                   │
     ┌───────────────────────────────┐                  │
     │  Analytical SQL Generation    │                  │
     │  - generator.py               │                  │
     └──────────────┬────────────────┘                  │
                    │                                   │
                    ▼                                   │
     ┌───────────────────────────────┐                  │
     │  SQL Validation & Guardrails  │                  │
     │  - validator.py               │                  │
     └──────────────┬────────────────┘                  │
                    │                                   │
                    ▼                                   │
     ┌───────────────────────────────┐                  │
     │  Database Query Execution     │                  │
     │  - executor.py (timeout guard)│                  │
     └──────────────┬────────────────┘                  │
                    │                                   │
                    ▼                                   │
     ┌───────────────────────────────┐                  │
     │  Grounded Insight Synthesis   │                  │
     │  - synthesizer.py             │                  │
     └──────────────┬────────────────┘                  │
                    │                                   │
                    └───────────────────┬───────────────┘
                                        │
                                        ▼
                         ┌────────────────────────────────────┐
                         │    Formatted Response Payload      │
                         │ (Answer, Data, Chart Config, Meta) │
                         └────────────────────────────────────┘
```

---

## 2. Core Architectural Principles

1. **Deterministic Grounding:** Queries are evaluated against empirical database tables and pre-computed analytical views. The LLM cannot invent metrics or numbers.
2. **Strict SQL Isolation & Read-Only Safety:** Only `SELECT` statements referencing approved tables are permitted. All DDL/DML operations (`DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `TRUNCATE`) are strictly blocked.
3. **Hybrid Predictive Routing:** Natural language questions concerning forecasting, segmentation, delay risk, or anomalies are routed directly to Phase 5 ML inference engines rather than generating raw ad-hoc SQL.
4. **Controlled Repair Loop:** If an SQL syntax error or execution fault occurs, the state machine invokes a repair node up to `MAX_SQL_RETRIES=2` before returning a safe user error.
5. **Observability:** Every request records latency, intent, generated SQL, column definitions, and visualization metadata formatted for future React frontend consumption.

---

## 3. Directory Structure

```
ai_analyst/
├── __init__.py
├── config/
│   └── ai_config.py            # Guardrails, timeouts, table allowlists
├── state/
│   └── agent_state.py          # Typed AgentState, Intent, and ResponseType definitions
├── schema_retriever/
│   └── schema_store.py         # Target schema metadata and table context
├── metrics/
│   └── metric_catalog.py       # Formal business formulas from METRIC_DEFINITIONS.md
├── planning/
│   └── query_planner.py        # Intermediate structured query plans
├── sql/
│   ├── generator.py            # NL2SQL generator with deterministic & LLM support
│   ├── validator.py            # AST/regex security validator & LIMIT injector
│   └── executor.py             # Read-only execution with timeout guardrails
├── security/
│   └── guardrails.py           # Prompt injection & administrative command defense
├── routing/
│   └── hybrid_router.py        # Routes predictive/forecasting queries to Phase 5 ML
├── insights/
│   └── synthesizer.py          # Factual answer formulation & chart recommendations
├── graph/
│   ├── nodes.py                # LangGraph node execution functions
│   ├── edges.py                # LangGraph conditional edge routing
│   └── workflow.py             # Compiled LangGraph StateGraph
└── service.py                  # AI Analyst master service orchestrator
```
