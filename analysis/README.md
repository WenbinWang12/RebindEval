# Public protocol summary

## Research question

Muon can behave differently from AdamW on tail-end associative-memory tasks. This project asks whether an optimizer-dependent difference persists when a model must reuse a learned computation under new values, renamed entities, counterfactual changes, or multi-step composition.

## Probe contract

| Probe | What changes | What it measures |
| --- | --- | --- |
| M | Nothing beyond the training task distribution | fitting and optimization speed |
| G1 | Numerical instances are new | transfer of the computation |
| G2 | Names are reassigned while the computation is paired | name-sensitive reuse |
| CF | A controlled value or relation is changed | use of current input |
| TwoHop | A learned relation is composed with another step | multi-step execution |

The primary comparison keeps the source checkpoint, data world, optimizer, seed, schedule, and evaluation contract explicit. Exact solution, valid derivation, and final-answer scores remain separate because an answer can be correct for different reasons.

## Release discipline

Every extension begins with a design file. Campaigns freeze code and data hashes before training. Results carry a scale label and an evidence status. Preliminary observations are kept separate from mechanism claims, and mechanism claims require a targeted intervention or a convergent diagnostic.

The four-scale extension designs in [`../designs_4scale/`](../designs_4scale/) cover iGSM multi-pass, prefix rescue, BioFacts/TwoHop, BioQA-tail, VarTrace coverage, GSM-Symbolic, and role-wise probes. The dataset card in [`../hf_dataset_cards/vartrace-v1/README.md`](../hf_dataset_cards/vartrace-v1/README.md) describes the rule-generated VarTrace benchmark and its scoring contract.

## Evidence status

The study is active. The public page is a readable index of the protocol and release surface. It does not substitute for the per-experiment reports, frozen manifests, or final paper tables.
