# AI Security & LLM Guardrails — Reference Notes

_Compiled November 2026 from current public sources (OWASP GenAI Security Project, EU institutions, vendor/framework documentation). Standards move fast — re-verify dates and rankings before quoting them._

## 1. What is a guardrail?

A guardrail is **a check plus an action**: inspect something (input, output, retrieved context, a tool call), then allow, block, modify, or escalate. Guardrails reduce risk; they do not remove it.

| Layer | Where it sits | Typical checks |
|---|---|---|
| Input | before the model | length, format, injection/jailbreak, PII, topic policy |
| Retrieval | between RAG store and prompt | source trust, tenant isolation, poisoned-document filtering |
| Dialogue / flow | around the conversation | stay on topic, scripted flows |
| Execution / tool | before an agent acts | allow-lists, argument validation, least privilege, human approval |
| Output | after the model | PII/secret leakage, toxicity, schema validation, safe rendering |

**Techniques, cheap → expensive:** regex/keyword rules → schema validation → ML classifiers → LLM-as-judge → human review. Production systems layer them so cheap checks exit early.

## 2. OWASP Top 10 for LLM Applications

### 2026 edition (released August 2026)
Ranking now blends a community vote (75%) with real incident data (25%, ~7.7k incidents).

| # | Risk | Note |
|---|---|---|
| LLM01 | Prompt Injection | direct or via retrieved content |
| LLM02 | Sensitive Information Disclosure | PII, credentials, proprietary data |
| LLM03 | Excessive Agency | up from #6 — too much permission/autonomy |
| LLM04 | Supply Chain | models, datasets, plugins, dependencies |
| LLM05 | Data and Model Poisoning | training / fine-tune / embedding data |
| LLM06 | Unbounded Consumption | cost, DoS, model extraction |
| LLM07 | Misinformation | wrong output treated as fact |
| LLM08 | Hidden Context Exposure | renamed from System Prompt Leakage |
| LLM09 | Vector and Embedding Weaknesses | RAG leakage, poisoned documents |
| LLM10 | Improper Output Handling | output → XSS/SSRF/command injection |

### 2025 edition (for reference — still widely cited)
1 Prompt Injection · 2 Sensitive Information Disclosure · 3 Supply Chain · 4 Data and Model Poisoning · 5 Improper Output Handling · 6 Excessive Agency · 7 System Prompt Leakage · 8 Vector and Embedding Weaknesses · 9 Misinformation · 10 Unbounded Consumption.

### OWASP Top 10 for Agentic Applications (2026, published 9 Dec 2025)
ASI01 Agent Goal Hijack · ASI02 Tool Misuse & Exploitation · ASI03 Identity & Privilege Abuse · ASI04 Agentic Supply Chain · ASI05 Unexpected Code Execution · ASI06 Memory & Context Poisoning · ASI07 Insecure Inter-Agent Communication · ASI08 Cascading Failures · ASI09 Human-Agent Trust Exploitation · ASI10 Rogue Agents.

Rule of thumb: if a system only *generates*, the LLM list is enough; once it can call tools, write to systems or hand work to other agents, **both lists apply**.

## 3. How this project maps to OWASP

| Risk | Covered here? | How / gap |
|---|---|---|
| LLM01 Prompt injection | Partial | phrase list in `guardrails.py`; no semantic or indirect-injection defence |
| LLM02 Sensitive disclosure | Partial | output substring check; no PII detection |
| LLM03 Excessive agency | N/A | the app has no tools/actions |
| LLM06 Unbounded consumption | Partial | 5000-char input cap; no rate limit/token budget |
| LLM08 Hidden context | Partial | blocks "reveal system prompt" phrasing; the app has no system prompt |
| LLM10 Improper output handling | Partial | UI uses `innerText` (safe against HTML injection); no schema validation |
| Others | No | no RAG, training or plugins in scope |

## 4. Tooling landscape (verify current status before adopting)

| Tool | Type | Strength |
|---|---|---|
| **NVIDIA NeMo Guardrails** | open source (Apache-2.0) | programmable rails in Colang; input/dialog/retrieval/execution/output rails; flow control |
| **Guardrails AI** | open source (Apache-2.0) | composable validators, structured/schema output validation |
| **Llama Guard (Meta)** | safety classifier model | classifies prompts/responses into hazard categories |
| **Prompt Guard / LlamaFirewall (Meta)** | classifier + agent guard | injection/jailbreak detection, agent-oriented checks |
| **Microsoft Presidio** | open source | PII detection/anonymisation |
| **LLM Guard (Protect AI)** | scanner library | input/output scanners — check maintenance status before use |
| **Azure Prompt Shields / AI Content Safety** | managed | injection + content moderation APIs |
| **Amazon Bedrock Guardrails** | managed | policy filters, PII, denied topics |
| **Lakera Guard** | managed (now part of Check Point) | prompt-attack screening |
| **Gemini safety settings** | built into the model API | configurable harm-category thresholds — complementary to custom guardrails |

Practical guidance from recent comparisons: use **different tools for different jobs** (flow control, classification, PII, schema validation) and avoid overlapping roles to keep latency low. Gateway-level enforcement is favoured in regulated environments.

## 4b. Frameworks & governance

- **NIST AI RMF** — Govern, Map, Measure, Manage; **NIST AI 600-1** is the Generative AI profile.
- **ISO/IEC 42001** — AI management-system standard.
- **MITRE ATLAS** — ATT&CK-style knowledge base of adversarial ML tactics and techniques.
- **EU AI Act** — risk-based law. In force 1 Aug 2024; prohibitions applied 2 Feb 2025; GPAI obligations 2 Aug 2025. Under the **Digital Omnibus on AI** (political agreement 7 May 2026) high-risk Annex III obligations move to **2 Dec 2027**, Annex I product-embedded to **2 Aug 2028**, and AI-generated-content labelling to **2 Dec 2026**. Confirm the final adopted text with counsel.
- OWASP lists are **not** compliance frameworks; they supply the named risks that NIST/ISO/EU obligations expect you to identify and treat.

## 5. Defence in depth for an LLM app (checklist)

1. Treat **all model input and output as untrusted**; separate instructions from data.
2. **Least privilege** for tools, credentials and data; short-lived scoped tokens.
3. **Human approval** for irreversible or high-impact actions.
4. Validate/encode output before it reaches a browser, shell, SQL engine or API.
5. **Never put secrets in prompts**; assume the system prompt can leak.
6. Rate-limit, set token/cost budgets and timeouts.
7. Isolate tenants in RAG; filter retrieved content; record provenance.
8. Pin and vet models, adapters, datasets and dependencies (ML-BOM / SBOM).
9. Log prompts, decisions, tool calls and blocks (mind PII) for audit and detection.
10. **Red-team continuously** and keep regression tests (this repo's `tests/`).
11. Measure guardrails: block rate, false-positive rate, bypass rate, latency overhead.

## 6. Real-world incidents worth knowing

- **EchoLeak (CVE-2025-32711)** — zero-click indirect prompt injection in Microsoft 365 Copilot that could exfiltrate internal data via a crafted email.
- **Bing Chat "Sydney" (2023)** — system prompt extracted via prompt injection.
- **Chevrolet dealership chatbot (2023)** — manipulated into agreeing to sell a vehicle for $1 (no real sale honoured).
- **Air Canada chatbot (2024)** — tribunal held the airline responsible for incorrect policy advice its chatbot gave (misinformation / accountability).
- **Samsung engineers & ChatGPT (2023)** — confidential code pasted into a public chatbot (data-leakage governance).

## 7. Sources consulted
OWASP GenAI Security Project (LLM Top 10 2025/2026, Agentic Top 10 2026); CyberSaint, Coralogix, HackerOne summaries of the OWASP lists; Council of the EU / Gibson Dunn / Taylor Wessing / Hogan Lovells on the Digital Omnibus on AI; Lima et al., *Defense-in-Depth for Generative AI: Architectural Evaluation and Comparison of LLM Guardrails*; vendor documentation and independent comparisons of NeMo Guardrails, Guardrails AI, Llama Guard and LLM Guard.
