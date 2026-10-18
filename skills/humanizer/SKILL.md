---
name: humanizer
description: Draft or revise prose to sound natural and appropriate to the user's voice. Use for humanizing text, removing robotic or corporate phrasing, polishing messages and documents, or auditing AI-style writing patterns.
metadata:
  version: "1.0.0"
---

# Humanizer

Write from the user's intent. Improve clarity, specificity, and rhythm while preserving meaning and voice. An already natural passage may need little or no editing.

## Establish the voice

Infer audience, medium, purpose, and level of formality from the request and source. Use the user's examples as voice evidence. If none are available, use direct, plain prose without forced friendliness. Ask only when missing context would materially change the message.

Apply explicit task instructions first, then these personal defaults:

- Do not introduce em dashes. Recast the sentence with a period, comma, colon, or parentheses as appropriate. In editable source prose, replace existing em dashes. Preserve them inside exact quotations and protected material, or when the user explicitly requests them. Do not substitute double hyphens or spaced en dashes as a workaround.
- Keep replies concise and lead with the point. Do not add explanations of the editing process unless requested.
- Avoid canned introductions, closing offers, repeated summaries, inflated praise, and unnecessary headings or bold labels. Remove formulas such as "I hope this message finds you well," "it is important to note," and "let me know if you need anything." Preserve specific requests, deadlines, and courtesy that serve the message; do not replace a generic closing offer with another one.

These are this user's preferences, not universal tests of human writing.

## Revise the substance and sentences

1. Identify what the reader needs to understand, decide, or do. Put that point early when the genre permits. Remove generic framing and repeated conclusions.
2. Preserve facts, names, dates, quantities, technical terms, attribution, uncertainty, and the strength of commitments. Do not turn an estimate into a promise, an association into a cause, or one person's view into consensus.
3. Preserve exact quotations, code, URLs, and required disclosures. Do not fabricate citations, anecdotes, feelings, personal experience, or missing details. When editing, do not add an addressee or signature absent from the source. For requested drafts and templates, use only supplied details or clearly requested placeholders. Keep intentional placeholders when the user is making a template; otherwise flag consequential gaps briefly instead of filling them in.
4. Rebuild awkward sentences instead of swapping synonyms. Prefer direct verbs and concrete subjects. Replace vague claims of significance with supported information, or remove the empty claim. Do not invent specifics to make prose sound more concrete.
5. Break habitual patterns: repeated sentence openings, generic transitions, unnecessary triplets, manufactured contrasts, trailing clauses that pretend to explain significance, and uniform paragraph shapes. Keep useful repetition and real contrasts.
6. Match the medium. Keep technical precision in expert writing, restraint in formal writing, and the user's regional English and natural shorthand. Do not manufacture personality with slang, typos, fragments, jokes, or random variation.

For substantial rewrites or explicit AI-style audits, read [the pattern reference](references/ai-writing-patterns.md). Use its general sections for ordinary prose. Read Wikipedia-specific guidance only for Wikipedia work. Short edits still require the final review below.

## Final review before returning text

Review the finished draft, not just the input. Repair any failures before responding:

- **Meaning:** Did any fact, qualification, attribution, deadline, request, or commitment change? Did the rewrite add anything unsupported?
- **Voice and structure:** Does this fit this person and medium? Remove generic hype, forced informality, fake intimacy, templated contrasts, repetitive transitions, and redundant conclusions. Keep useful structure and necessary courtesy.
- **Punctuation and residue:** Check for em dashes according to the personal default above. Remove assistant chatter, editing instructions, leaked tool markers, and accidental formatting. Do not damage valid quotations, citations, or markup.
- **Economy:** Does each sentence contribute? Read for natural flow without forcing every sentence into the same length or shape. Stop when the text is clear and faithful; do not keep polishing away the user's voice.

## Return the result

Return the edited or drafted text directly, without a preamble, code fence, or closing offer. Preserve useful formatting. For an audit request, give specific findings and suggested fixes instead of silently replacing the entire text. For light editing, change only what needs work; for drafting, use the requested length and format.

Keep roughly the source length unless the user requests a different length or padding needs removing. Provide alternatives only when asked or when ambiguity makes them useful. If an unresolved factual or meaning issue matters, add a short note after the text. Do not fact-check every link as part of an ordinary style edit or claim verification you did not perform; investigate when requested or necessary to resolve a material issue.

Treat pattern lists as diagnostic aids, not word blacklists or proof of authorship. Never promise detector evasion. Preserve required authorship and AI-use disclosures.
