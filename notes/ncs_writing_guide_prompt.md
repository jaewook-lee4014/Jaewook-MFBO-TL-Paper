# Nature-family (NCS) writing guide — paste-ready LLM prompt block

Compiled 2026-09-15 from Nature Computational Science / Nature Portfolio author
guidance, Nature-family editorials on writing, and the register of published NCS /
Nature Communications papers on Bayesian optimization, multi-fidelity and
transfer learning. Section A is the block to paste into an LLM prompt. Section B
adds manuscript-specific constraints. Section C lists observations and sources.

---

## A. PROMPT BLOCK (paste as-is)

You are revising a research Article for Nature Computational Science (a Nature
Portfolio journal). Apply the following house conventions. Improve narrative flow,
paragraph structure, sentence construction and wording ONLY; never add, remove or
strengthen a scientific claim, number, or comparison that is not already in the
text, and never change what a figure is said to show.

### 1. Format and limits (NCS Article)
- Sections and headings: Introduction, Results, Discussion, Methods. Results and
  Methods are divided by topical subheadings; the Discussion has NO subheadings.
- Abstract: one unstructured paragraph, 100–150 words, no references, no
  non-essential numbers or abbreviations.
- Main text (Introduction + Results + Discussion) up to 3,500 words; up to 6 display
  items (figures + tables); Methods separate and as concise as replication allows.
- Title: a noun phrase (not a full declarative sentence in this field), ideally
  <= 75 characters, no acronyms, no method names, no numbers, no question mark, no
  puns; outcome-first rather than method-first; specific about the message.
- Spelling per Oxford English Dictionary (British) unless a US spelling is the field
  standard; consistent throughout.
- Every figure and table is cited in numerical order; panels in alphabetical order.

### 2. One-message architecture
- The paper carries ONE message, stated in the title, restated in the "Here we"
  sentence of the abstract, supported by every Results subsection, and returned to
  in the Discussion. Delete or demote anything that does not serve it.
- Context–Content–Conclusion at every scale: the Introduction sets the context, the
  Results are the content, the Discussion brings home the conclusion; each paragraph
  opens with context (topic sentence), develops one idea, ends with its conclusion.
- Each subject is treated in exactly one place (no zig-zag between sections);
  parallel content uses parallel constructions.
- Main text carries the load; anything needed to support but not to tell the story
  goes to Methods or Supplementary Information.

### 3. Abstract skeleton (Nature summary paragraph, 6–8 sentences)
1. One or two sentences of basic introduction to the field, comprehensible to a
   scientist in any discipline.
2. Two or three sentences of more detailed background for scientists in related
   disciplines.
3. One sentence stating the general problem or gap (typically opens with
   "However" or "Despite").
4. One sentence with the main result, introduced by "Here we show / introduce /
   provide / investigate".
5. Two or three sentences on what the result reveals in direct comparison with what
   was previously thought or done; include one or two key quantitative facts
   (e.g. "up to N-fold", "on every X benchmark") but no flood of numbers.
6. One or two sentences placing the result in a broader context; implications stated
   realistically ("may help guide", "provides a basis for").
- Results in the abstract are in the present tense. Methods appear only if the
  method is itself the contribution.

### 4. Introduction
- A funnel of progressively more specific paragraphs: field -> specific background ->
  explicit gap -> what this work does. Explain the research question early; do not
  assume the reader has the specialist background.
- The last paragraph states what was done and previews the main findings in the
  order the Results present them. Do not start the paper with "In this paper we".

### 5. Results
- One subsection per major finding, each tied to one figure or panel group, in
  order of importance. Subheadings are short topical phrases (in NCS mostly
  gerund/noun phrases such as "Finding suitable scenarios for MFBO",
  "Understanding model limitations"; declarative findings are acceptable) —
  keep ONE grammar for all subheadings.
- Each Results paragraph: topic sentence giving the rationale or the claim -> the
  evidence with figure reference (present tense for what the figure shows, past tense
  for what was done) -> one sentence of direct interpretation or transition. No
  extended interpretation, no new context, no repetition of numbers already in the
  figure — the text summarises what the display item shows.
- State the protocol once in one blanket sentence ("In all cases, experiments are run
  for N independent seeds; error bars are ...") and do not re-state it per paragraph.
- Quantitative claims: name the benchmark, the metric, the comparator and the
  magnitude ("on the COFs, FreeSolv and polarizability tasks, ... 0.68, 0.59 and
  0.56"); ranges or ceilings ("up to N-fold", "9–33 %") rather than a single
  cherry-picked number; "X of Y benchmarks" for counts.
- Superiority/parity wording used in this venue: "consistently outperforms",
  "matches or exceeds", "comparable to" (applied locally, never as a blanket
  verdict), "competitive with ... but still outperformed by", "loses its advantage
  when ...". Avoid "on par with", "significantly" in a non-statistical sense, and
  "dramatically".
- Mixed or negative results are written as conditions, not as failures: say WHEN the
  method wins and WHEN it loses, and tie both to the same explanatory variables
  ("the favourable trend is reverted when ...", "although X achieves near-perfect
  performance on ..., it exhibits fundamental limitations in ..."). Never omit the
  losses.
- Compute/cost claims are stated as a metric with the comparison basis made
  explicit (equal accuracy or equal budget; hardware named) and never as a
  throwaway adjective.

### 6. Discussion (no subheadings)
- Open by re-placing the result in broad context (what the field now knows), not
  with a recap of numbers. Then, in order of importance: what the findings mean,
  how they compare with prior work (name the prior work concretely), alternative
  explanations considered, limitations, implications and one or two sentences of
  future work.
- The majority of the Discussion is interpretation; do not repeat Results, do not
  report new data.
- Limitations are stated in author voice as concessive sentences ("Although ...,
  ...", "A limitation of this approach is that ...") and are specific (which
  benchmarks, which settings, which assumptions), not generic.
- Speculate sparingly and mark speculation ("These results suggest", "may enable",
  "is consistent with"); measured results themselves stay unhedged.
- Recommendations to practitioners are operationalised as concrete conditions
  ("we recommend ... when R^2 > 0.8 and rho < 0.1"), not as slogans.

### 7. Methods
- Open plainly ("BO uses a probabilistic surrogate model and an acquisition function
  to ..."), then become specific fast: every setting a reader needs to replicate
  (architectures, hyperparameters, optimisers, budgets, schedules, seeds, hardware,
  software versions), with the reason for each non-obvious choice.
- Describe the method as it is, never its development history or superseded
  variants.
- Include Data availability and Code availability statements (repository URL,
  DOI-minting archive such as Zenodo, licence, "includes instructions to run all
  experiments described in this work").

### 8. Sentence-level style
- Active voice and "we" for what the authors did; direct, simple constructions;
  10–20-word sentences; one idea per sentence.
- Old-to-new information flow: put the known idea in the topic position at the
  start of a sentence and the new, important idea in the stress position at the end;
  the stress position of one sentence sets up the topic of the next. The passive is
  allowed when it achieves this link.
- Tense: past for what was done and found; present for what figures/tables show
  and for established knowledge; present for abstract results.
- Every word does work: cut "it is worth noting that", "interestingly", "it should
  be mentioned", nominalisations ("implementation of" -> "we implemented"),
  stacked caveats and ornamental adjectives.
- Define every abbreviation at first use in abstract, main text and Methods
  separately; keep abbreviations to a minimum; use pronouns rather than repeating
  the acronym; keep technical terms where they are needed and explain them
  when unavoidable.
- Confident but factual: replace defensive framing ("though not exhaustive, this
  paper provides a useful ...") with a direct statement of what was done and shown.

### 9. Expression bank (characteristic of Nature-family papers)
- Abstract: "X is a promising framework to ..."; "However/Despite ..., there is a
  lack of ..."; "Here we show/introduce/provide/investigate ..."; "We find that ...";
  "Our results may help guide ...".
- Results: "To determine whether ..., we ..."; "Across N benchmarks ..."; "On every
  ... benchmark ..."; "the best ... matches or exceeds ..."; "In contrast, ...";
  "Consistent with ..."; "This advantage tracks ... more strongly than ...";
  "loses its advantage when ...".
- Discussion: "Taken together, these results ..."; "We attribute this to ...";
  "These findings suggest/indicate/establish ..."; "Although ..., ..."; "A natural
  next step is ..."; "Therefore we recommend ... as a guiding principle".
- Legends: first sentence is a brief title for the whole figure, preferably a
  claim ("MFBO results depend on problem conditions."), followed by what each
  panel depicts, then n, error-bar definition and any statistic; legends describe,
  they do not interpret or give methods.

### 10. Banned or discouraged wording (and why)
- "novel", "new", "first", "for the first time", "unprecedented", "paradigm
  (shift)", "state-of-the-art" as self-description, "groundbreaking", "highly
  rigorous", "a major step forward", "crucially": Nature-family policy asks authors
  to remove primacy claims and self-laudatory language because they are unverifiable
  and obscure the evidence; NCS itself: "no paradigm shifts, please".
- "significant(ly)" without a statistical test; "dramatically", "remarkably",
  "interestingly" without concrete justification.
- Question-mark titles, puns, and mixing subheading grammars.
- Any sentence that recaps a result inside the Discussion instead of interpreting it.

### 11. What NCS reviewers most often ask for (pre-empt in the text)
- Breadth and rigour of benchmark comparisons; recent state-of-the-art baselines
  present; metrics justified as appropriate; comparisons over sufficiently large and
  diverse datasets.
- How every tool/baseline was configured and parameterised, and why.
- Reproducibility: seeds, hardware, software versions, data curation steps, exact
  n per condition, error bars defined in every legend.
- A sufficient, specific discussion of limitations.
- Figures explained well enough that a non-specialist sees why each matters;
  no selectively reported results; claims consistent with the evidence;
  no over-confidence in conclusions.
- Accessibility to readers outside the sub-field and to non-native English readers.

### 12. Self-check before returning the revision
- Does the title, the "Here we" sentence, every Results subheading and the first
  Discussion paragraph state the SAME message?
- Is every number in the abstract and Discussion present, identically, in a figure,
  table or Results sentence?
- Is every claim conditional on the settings under which it was shown?
- Is each abbreviation defined; are all subheadings of one grammar; are figures
  cited in order; is the word budget respected?

---

## B. MANUSCRIPT-SPECIFIC CONSTRAINTS (append to the prompt for this paper)

- Only ONE run set exists for the reader: never mention earlier runs, earlier
  designs, the internal repository, development history, or dates/provenance;
  never contrast the current method with a superseded variant ("however, X is not
  used"). State the method as it is and the reason as what the design provides.
- Surrogates: five transfer-learning surrogates (Frozen-representation transfer,
  PtJ, E2E, Soft, MMD) versus three Gaussian-process methods; never "nine" or
  "eleven", no "paradigms", no fine-tuning language.
- No p-values, no significance tests; report seeds and mean/dispersion as the
  figures do (40 pooled seeds; HOPV15 budget 45, Matbench-gap budget 100).
- Table 1 lists raw descriptor dimensions (210/132/14) and notes the PCA step.
- Keep the Fig. 1/2 conventions everywhere: Table 1 benchmark names (e.g.
  "Matbench-gap"), Fig. 1 abbreviations and footnote, GP orange / TL blue.
- Do not touch numbers, claim strength, or figure descriptions; wording only.
- Cite Sabanza-Gil et al. as Nature Computational Science 5, 572–581 (2025).

---

## C. Notes on the current manuscript (2026-09-15) and sources

Observations to feed the revision:
- Title "Transfer Learning Architectures for Scalable Multi-Fidelity Bayesian
  Optimization ..." is long and method-first; NCS chemistry/BO titles are short
  outcome-first noun phrases without acronyms (Nature's own limit is 75 characters).
- Results subheadings mix declarative sentences ("Gaussian processes perform best on
  ..."), a question ("When is a surrogate necessary?") and a bare noun ("Computational
  cost"); NCS practice is one grammar throughout (topical phrases or declaratives).
- The abstract already follows the summary-paragraph template (context -> problem ->
  "Here we investigate" -> results -> implication) at ~150 words; keep it so.
- The Discussion opens with a restatement of the finding; NCS Discussions usually
  re-open with broad context and then interpret.
- Optional editorial point: NCS "Analysis" articles are defined as "systematic
  comparisons of computational methods and tools of high importance for a field";
  a surrogate benchmark may fit that format at least as well as "Article".

Sources (nature.com pages were partly behind a login wall, so some limits came
from search-indexed text — verify limits on the NCS submission-guidelines page
before final formatting):
- nature.com/natcomputsci/submission-guidelines, /content, /aims,
  /submission-guidelines/writing-and-language, /editorial-policies/reporting-standards
- nature.com/nature/for-authors/formatting-guide;
  nature.com/documents/nature-summary-paragraph.pdf;
  nature.com/nature-portfolio/for-authors/write;
  nature.com/nature/for-authors/editorial-criteria-and-processes
- Nature 555, 129 (2018) "How to write a first-class paper" (d41586-018-02404-4)
- Nature Methods editorial "So you're writing a paper" (nmeth.4532)
- Nature Cancer "First, novel and paradigm-shifting" (s43018-023-00685-x);
  Nature Human Behaviour "Not the first, not the best" (s41562-021-01068-x)
- NCS editorials: "What reviewers request the most" (s43588-026-00989-9);
  "Dos and don'ts in a cover letter" (s43588-022-00348-4); "Moving towards
  reproducible machine learning" (s43588-021-00152-6); "Seamless sharing and peer
  review of code" (s43588-022-00388-w); Analysis format (s43588-023-00588-y)
- Exemplar papers: Sabanza-Gil et al. NCS 2025 (s43588-025-00822-9);
  Alampara et al. NCS 2025 (s43588-025-00836-3); Chen & Ong NCS 2021
  (s43588-020-00002-x); van Tilborg & Grisoni NCS 2024 (s43588-024-00697-2);
  Buterez et al. Nat. Commun. 2024 (s41467-024-45566-8); Jha et al. Nat. Commun.
  2019 (s41467-019-13297-w); Wang et al. Nat. Commun. 2023 (s41467-023-41948-6);
  Volk & Abolhasani Nat. Commun. 2024 (s41467-024-45569-5); McGreivy & Hakim
  Nat. Mach. Intell. 2024 (s42256-024-00897-5)
- Mensh & Kording, "Ten simple rules for structuring papers", PLoS Comput. Biol.
  2017; Springer Nature "Writing a manuscript" campaign pages.
