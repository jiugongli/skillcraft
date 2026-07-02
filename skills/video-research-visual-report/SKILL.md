---
name: "video-research-visual-report"
description: "Use when the user wants to turn a video link into a deep researched review and visual report: extract transcript/audio, find original sources, browse external opinions, compare supporting and opposing views, perform adversarial analysis, then produce text commentary plus information images, long image, or PPT depending on content density."
---

# Video Research Visual Report

Use this skill for video-driven research reports where the output should include both analysis and visual explanation.

## Workflow

1. **Understand the video**
   - Get subtitles/transcript first.
   - If subtitles are unavailable, extract audio and transcribe it.
   - Do not rely only on the title, description, comments, or danmaku.
   - If the video cites an article, report, paper, dataset, product page, or official source, locate and read the original source.
   - Separate video author claims, cited-source claims, facts, and speculation.

2. **Cross-check externally**
   - Browse for official sources, third-party analysis, user/community feedback, and dissenting views.
   - For current products, prices, benchmarks, laws, markets, or model releases, verify with up-to-date sources.
   - Do not fully trust the video author or any single source.
   - Mark what is confirmed, disputed, inferred, or still uncertain.

3. **Structure the debate**
   - Extract the video's central claims.
   - Organize supporting, opposing, and conditional/neutral views.
   - Compare by dimensions such as capability, cost, UX, ecosystem, risk, data quality, benchmark validity, and practical fit.

4. **Adversarial pass**
   - Do 2-3 rounds before concluding:
     - Challenge the video: what is exaggerated, omitted, or selectively quoted?
     - Challenge the original source/official data: what incentives or benchmark choices may bias it?
     - Challenge practical relevance: would a real user reach the same conclusion?
   - Only summarize the outcome; do not expose long internal reasoning.

5. **Text review**
   - Provide a concise overall judgment.
   - Then give dimension-by-dimension analysis.
   - End with practical recommendations by scenario, not a single absolute winner.
   - State uncertainty and residual risk.

6. **Choose output format**
   - Decide based on video length, information density, and user goal.
   - Simple content: 3-6 information images.
   - Medium complexity: 6-10 information images.
   - Complex or controversial content: 10-20 images or multiple chapters.
   - For reports or talks, use PPT-style pages.
   - For social sharing, use a vertical long image or multiple short images.
   - Do not force everything into one long image when chapters would be clearer.

7. **Visual requirements**
   - Each image/page must have a title, short explanation, and clear point.
   - Avoid mood-only images.
   - Use deterministic local layout for critical text and numbers; do not rely on image generation for dense Chinese text.
   - If generated illustrations are useful, use them only as visual support and overlay verified text afterward.
   - Include source categories where relevant: video transcript, original source, official docs, third-party analysis, community feedback.

8. **Long image requirements**
   - Recommended order:
     - `00`: explainer page
     - `01`: problem definition / overview
     - `02`: video core claims
     - `03`: original-source claims
     - middle pages: dimensions, evidence, debate
     - final pages: adversarial conclusion and action guidance
   - `00` must explain what the report is based on, what it is trying to clarify, and how to read it.
   - Leave safe margins on all sides.
   - After merging, generate a preview and inspect for cropped right/bottom text.
   - Run edge checks or OCR when cropping risk is suspected.

9. **Final delivery**
   - Include the text review.
   - Include paths to single images/PPT and long image if generated.
   - Include source links used.
   - Include known uncertainty.

## References

- Use `references/prompt-template.md` when the user wants a reusable prompt.
- Use `references/research-checklist.md` to keep research coverage consistent.
- Use `references/output-formats.md` when choosing long image vs short images vs PPT.
