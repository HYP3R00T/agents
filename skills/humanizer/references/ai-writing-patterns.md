# AI-writing pattern reference

Use this checklist to diagnose and revise prose. It is adapted from Wikipedia's “Signs of AI writing” field guide as reviewed on 2026-10-18: <https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing>.

The source is descriptive, not prescriptive. These features are clues only when they are unnecessary, inaccurate, formulaic, or unusually concentrated. Do not flatten a writer's voice merely to eliminate every possible clue.

For ordinary messages and documents, use the general guidance below. The final section applies only to Wikipedia work. This reference supports the personal preferences and final review in `SKILL.md`; it does not override them.

## Content and reasoning

- Inflated significance: unsupported claims about legacy, symbolism, historical importance, broader trends, turning points, or an “evolving landscape.”
- Canned notability: insisting that a person or organization received independent, regional, national, trade, or prominent media coverage instead of explaining what reliable sources reported.
- Superficial analysis: attaching generic interpretation to facts, often through trailing “-ing” clauses about highlighting, reflecting, ensuring, fostering, or contributing.
- Promotional language: press-release, corporate, résumé, product-copy, or travel-brochure prose; repeated praise of heritage, natural beauty, innovation, excellence, commitment, or impact.
- Vague connections: saying that subjects are associated, connected, or linked without explaining the supported relationship. Name the relationship when the source provides it; otherwise preserve uncertainty or flag the gap.
- Vague authority: “experts,” “observers,” “critics,” “industry reports,” or “several sources” without specific and accurate attribution.
- Overgeneralization: turning one or two views into a consensus or implying that a complete list is only a sample.
- Formulaic endings: rigid “Challenges,” “Legacy,” or “Future outlook” sections that acknowledge problems and finish with vague optimism or speculation.
- Reified titles: defining a list or broad article title as if the title itself were a real-world entity.

## Language and grammar

- Watch for an unusual concentration of: additionally, align with, boasts, bolstered, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight, interplay, intricate, intricacies, key, landscape, meticulous, meticulously, pivotal, robust, showcase, tapestry, testament, underscore, valuable, and vibrant.
- Watch for generic significance formulas: serves or stands as, testament or reminder, crucial or pivotal role, underscores its importance, reflects broader, enduring legacy, setting the stage, shaping the landscape, focal point, deeply rooted, and indelible mark.
- Watch for promotional formulas: boasts, rich, profound, exemplifies, commitment to, nestled, in the heart of, groundbreaking, renowned, featuring, and diverse array.
- Prefer a plain copula or “has” when accurate. Do not reflexively replace “is,” “are,” or “has” with serves as, stands as, marks, functions as, operates as, represents, boasts, features, maintains, or offers.
- Avoid serial negative parallelisms that manufacture contrast: “not just X but Y,” “not X but Y,” and “X rather than Y.” Keep a contrast when the distinction is real.
- Break the automatic rule of three. Use the number of examples or adjectives the idea requires.
- Avoid elegant variation: do not cycle through strained synonyms solely to prevent natural repetition.
- Avoid generic transitions at the start of successive sentences, especially repeated “Additionally,” “Consequently,” and “Notably.”

## Style and formatting

- Avoid title case for every heading unless the house style requires it.
- Avoid mechanical bolding, especially repeated keywords and “key takeaway” formatting.
- Avoid vertical lists made of bold mini-headings plus colons when ordinary prose is clearer.
- Follow the personal punctuation default in `SKILL.md`: do not introduce em dashes, and recast editable source prose that contains them. Keep exact quotations and explicit user exceptions intact.
- Do not decorate headings or bullets with emoji unless the user's medium and voice call for it.
- Do not create tiny or unnecessary tables when a sentence or short list is clearer.
- Follow the medium's quotation-mark style; never introduce inconsistent straight and curly quotation marks.
- Keep heading levels sequential and omit decorative thematic breaks before each heading.

## Chatbot residue and scaffolding

- Remove assistant chatter such as “Of course,” “Certainly,” “I hope this helps,” “Here is a detailed breakdown,” “Would you like,” and “Let me know.”
- Remove statements that the draft is intended for Wikipedia or that explain how the user should paste, submit, customize, or expand it.
- Remove knowledge-cutoff disclaimers and unsupported speculation based on “available information,” “provided sources,” scarce details, or limited search results.
- In finished prose, flag or remove unintended fill-in-the-blank names, bracketed instructions, placeholder URLs, `YYYY-XX-XX` dates, and comments telling a future editor what to add. Preserve intentional placeholders in requested templates; never fill gaps by inventing details.
- Use the target platform's markup. Do not leave Markdown in wikitext, broken templates, skipped headings, or code fences around prose.
- Remove leaked tool markers: `contentReference`, `oaicite`, `oai_citation`, `turn0search0`, `attributableIndex`, `[cite: 1]`, `[span_1](start_span)`, `grok_card`, `grok_render_citation_card_json`, DeepSeek lenticular-bracket/dagger citations, `[attached_file:1]`, `ppl-ai-file-upload`, and `:::writing` wrappers.
- Never invent categories, templates, template parameters, policy shortcuts, citations, or reference syntax.

## Sources and factual integrity

- Preserve valid citations, links, and the scope of the claims they support. Never invent sources or imply that a citation was verified when it was not.
- When fact-checking is requested or a material citation problem needs resolving, verify that the source supports the claim and check identifiers such as DOIs against the cited work. Flag anything unresolved.
- Do not remove necessary uncertainty or disclosure language as mere chatbot residue. Distinguish empty disclaimers from meaningful limits on evidence.

## Human texture worth preserving

- Simple “is,” “are,” and “has” constructions.
- Direct verbs such as wrote, moved, used, tried, and died when they are accurate and appropriate.
- Supported definitive statements, ordinary hedges, intensifiers, and occasional wordiness.
- Natural repetition, uneven sentence lengths, restrained fragments, idiom, regional spelling, and domain-specific shorthand.

## Do not use as evidence by itself

Perfect grammar, mixed registers, bland prose, formal or academic language, transition words in isolation, missing citations, correct wikitext, and random markup mistakes do not establish AI authorship. Humanize the prose because it reads poorly for its purpose, not to satisfy an unreliable detector.

## Wikipedia-specific checks

Use only for Wikipedia articles, discussions, edit summaries, and profiles. General correspondence does not need encyclopedia conventions.

### Sources and citations

- Verify that links resolve and that each source supports the nearby claim.
- Check ISBN and DOI validity; confirm that a DOI leads to the cited work rather than an unrelated paper.
- Give usable page numbers for books when the claim depends on a specific passage.
- Preserve valid citation style and reference reuse syntax.
- Remove AI-service tracking parameters such as `utm_source=chatgpt.com`, `utm_source=openai`, `utm_source=copilot.com`, or `referrer=grok.com` when they are not required.
- Do not declare named references that are unused or invoke names that were never defined.

### Discussions, profiles, and edit summaries

- Avoid long, sectioned comments that read like formal reports when a direct reply will do.
- Do not misquote rules, transclude banners casually, or invent policy shortcuts.
- Do not repeatedly assure readers that a draft complies with rules, is neutral, or uses reliable sources. Demonstrate those qualities in the work.
- Keep edit summaries brief and specific to what changed. Avoid first-person essays, policy recitations, stacked assurances, and vague claims of improved clarity or tone.
- Do not mention untouched information that was “preserved” or “retained” unless that fact matters.
- Describe the information added, not merely the presence of sources or citations.
- Do not state the obvious by announcing that reviewer feedback was addressed.
- Avoid generic user-page sections such as “About Me,” “My Interests,” and “Let's Connect” paired with emoji and canned collaboration language.

### Historical and contextual signs

- Remove didactic throat-clearing such as “it is important to note,” “it is crucial to remember,” and “worth noting” when the sentence can state the point directly.
- Remove automatic “In summary,” “Overall,” or “In conclusion” passages that merely repeat the preceding section.
- Remove chatbot refusals, apologies, and self-identification unless the conversation specifically requires them.
- Check for abrupt cutoffs and suspiciously stale access dates.
- Keep the writer's established variety of English and level of formality unless asked to change them. Avoid unexplained shifts in voice.
- Do not add submission statements, pre-declined review templates, irrelevant maintenance tags, or protection templates.
