# Dev log — Seeing Machines (L1–L3)

Chronological iteration history across the three levels. Kept honest: the failed runs
are here on purpose, because they are the evidence behind later decisions.

---

## L1 — The Finder

**Embedding.** Encoded the ~195-image personal archive with `siglip-base-patch16-224` on a
T4 GPU (batch 16), L2-normalised, cached to a pickle. All retrieval then runs on CPU.

**Retrieval atlas.** Ran 15 queries across four categories, recording top-5 files, scores,
and a mechanistic reading of each. Built the score-distribution study (strong vs weak
queries) and set a **retrieval threshold ≈ 0.08**.

**Findings that became the L2 brief.** SigLIP encodes scenes, not identity/age; counting and
relations fail (`two people together`, top 0.0598); concrete beats abstract; scores compress
into 0.03–0.13 on this homogeneous single-subject corpus.

---

## L2 — The Companion

### [2026-07-03] Captioning — parse bug (0/0)
Three attempts with `google/gemma-3-4b-it` (4-bit), structured-JSON schema, deterministic
decode (`do_sample=False`). **JSON-parse success 0/0** each time — a silent parse bug; no
captions were produced. Path/parsing errors identified and fixed.

### [2026-07-06 22:03] Captioning — clean run (227/227)
Re-ran the fixed pipeline top-to-bottom on the coherent 227-image set.
**JSON-parse success 227/227.** Schema fields match the notebook exactly.

### [2026-07-06 22:03] Caption embeddings
Embedded the 227 `searchable_text` fields with `all-MiniLM-L6-v2`.
Shape **(227, 384)**, L2-normalised → `text_embeddings.pkl`.

### [2026-07-08 21:27] Captioning — scale-up attempt (628/1462)
Tried to scale to the full 1462-image dump. **JSON-parse success 628/1462 (~43%)** — the
structured-JSON captioner is brittle at that volume. Kept the run as
`captions_1462_backup.json` (in the L2 history) as evidence; **decision: stay on the coherent
227.** Lesson carried into L3: run one pipeline top-to-bottom on a set you trust rather than
stitching bigger, dirtier runs.

### Route comparison
Ran 6 shared probe queries through both routes → `l2_route_comparison.json`. Caption route
returns far higher similarities (0.28–0.70) than CLIP (0.06–0.13) and, more importantly,
often picks **different** images. Where they agree (`a kid fishing` → same 2006 photo), trust
it; where they disagree (`a formal event` → caption finds the real ceremony), caption is the
better human match. Neither wins alone → motivates L3 fusion.

---

## L3 — The Critic

### Hybrid fusion
The two routes are in different spaces (SigLIP 768-d images, MiniLM 384-d caption text) with
different query encoders, so fusion is done at the **score level**: min-max normalise each
similarity vector over the corpus, then `hybrid = α·visual + (1−α)·caption`.

### α-sweep
Swept α from 0.0 (pure caption) to 1.0 (pure visual), scoring precision@5 on the gold set.
**Best α = 0.3, precision@5 = 0.575** → `alpha_sweep.json`. Pure visual collapses to 0.225;
pure caption sits at 0.500; the fused middle beats both ends.

### Gold set + evaluation
Assembled 8 gold queries with relevant filenames **auto-derived from caption fields and
filename dates, then eyeballed — not exhaustively hand-verified** (recorded in each
`gold_queries.json` entry). Scored precision@{1,3,5} for all three routes →
`evaluation_results.json`:

| route | P@1 | P@3 | P@5 |
|---|--:|--:|--:|
| visual only | 0.500 | 0.250 | 0.225 |
| caption only | 0.625 | 0.500 | 0.500 |
| hybrid (α=0.3) | 0.875 | 0.625 | 0.575 |

Per-query: hybrid rescues age queries, ties on travel/formal, and cannot save queries where
both routes are already weak.

### Multimodal grounding + degradation
Passed retrieved images (capped 3–4) into Gemma at answer time → `multimodal_degradation.json`.
Decisive at 1 image, hedged at 4 ("I can't determine a single overarching setting"). More
visual context buys breadth, costs commitment.

---

## Open items
- Add a 20-image corpus sample under `corpus/sample/` (see `corpus/README.md`).
- Optional: hand-verify the gold set and/or expand it beyond 8 queries for tighter numbers.
- Optional: per-query or learned α instead of a single global weight.
