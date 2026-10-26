# humanizer

Draft or revise prose to sound natural and fit the user's voice while preserving meaning and facts.

[Explore the skill folder](https://github.com/HYP3R00T/agents/tree/main/skills/humanizer) · [Read SKILL.md](https://github.com/HYP3R00T/agents/blob/main/skills/humanizer/SKILL.md)

## When to use it

Use it to polish messages and documents, remove robotic or corporate phrasing, draft from supplied details, or audit AI-style writing patterns.

```text
$humanizer Lightly edit this message while keeping my voice: ...
$humanizer Draft a concise email using these details: ...
$humanizer Audit this passage for repetitive or generic phrasing: ...
```

Provide the source text or drafting details. Audience, purpose, tone, and examples of your writing help when they would change the result. Already natural text may need little or no editing.

## What it does

- Leads with the point and removes generic framing, padding, and repeated conclusions.
- Improves clarity and sentence flow without inventing facts, experiences, feelings, or commitments.
- Preserves qualifications, technical terms, attribution, quotations, code, URLs, and required disclosures.
- Matches the audience and medium, including regional English and natural shorthand.
- Reviews the finished text for meaning, voice, punctuation, and unnecessary wording.

For substantial rewrites and explicit audits, it uses the accompanying writing-pattern reference. Keep the complete skill folder, including `references/`, together when installing it. No additional CLI tools are required.

## Defaults and output

The skill defaults to concise, direct prose, avoids introducing em dashes, and removes canned introductions and closing offers. These are personal preferences; explicit task instructions take priority.

Editing and drafting return the resulting text directly, preserving useful formatting. Audits return specific findings and suggested fixes. Light edits change only what needs work; other rewrites stay roughly the source length unless requested otherwise or padding needs removing.

## Boundaries

The skill does not fabricate missing details, add unsupported claims, or silently strengthen uncertainty into certainty. It preserves required authorship and AI-use disclosures and does not promise detector evasion. Writing-pattern lists are diagnostic aids, not proof of authorship.

Ordinary style edits do not automatically fact-check every link. Consequential gaps or unresolved meaning issues may receive a short note.

Unlike explicitly triggered workflow skills, humanizer permits automatic selection for relevant writing requests. `SKILL.md` is the source of truth for its full instructions.
