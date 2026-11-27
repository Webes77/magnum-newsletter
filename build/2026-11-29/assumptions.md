# Assumptions and working notes, This Week in AI, 29 November 2026

Draft run Saturday 28 Nov 2026, 6am Gold Coast. Covered window: Sat 21 Nov to Fri 27 Nov 2026 (Gmail after:2026/11/21 before:2026/11/28). 35 threads, all read in full by two reading passes. Skipped as not newsletter material: dm@danmartell.com, hey@eliotprince.com. Promos noted and not used: Rob Howard "Build an AI Company Brain with me" and "Black Friday at Innovating with AI", Ruben Hassid "Last call.", DeepLearning.AI course promo.

All pictures and the video were made on fal (standing change of 22 Nov: no Higgsfield).

## Step 1B: what the big newsletters all do (The Rundown, Superhuman, Evolving AI)
1. A short greeting, then the lead story's sharpest fact in the next line. "Welcome back, Superhuman. Apple's iconic slogan "There's an app for that" dominated the 2010s. Anthropic just one-upped them." / "Good morning, AI enthusiasts... Few fields have changed more under AI this past year than math."
2. Headlines are subject, verb, result, in plain words. "OpenAI pays locals to bring AI to small businesses"; "Claude Can Now Turn Ideas Into Installable Apps."
3. First sentence of a story carries who, what and a number or date.
4. Short warm sign-off with names, no pitch. "See you soon, Rowan, Zach..." / "Until next time, Zain, Theodore..."
Applied: opener opens on the Win's sharpest true detail; headlines subject-verb-result; leads open on who, what and date. Difference: all three led on industry news (Riemann proof, Nvidia, Anthropic IPO). Our rule picks for the reader, so none of those run. Noted for James, no change made.

## Choices made because nobody could be asked
- The Win: first unused Win bank entry, Fireflies 01M6MW0ZKYAGNNV2JQXH8WWPS9 (5 Nov 2026), from about 23:35 to 24:50 in the recording. The client services manager of a coaching and seminar business says a client document she had worked on for three weeks was done after four hours one evening talking it out with AI, then put through all her clients; she says she could double her client load; humans stay the final sign-off. Written without names, figures (weeks and one evening only, "a lot more clients") or town. What the document covered is not said in the transcript, so the page does not say. Not a repeat: no coaching or seminar Win in issues/. Add this id to the Win bank's Used list in ROUTINE.md (this run never pushes to main, so it is left for the Sunday run or a session).
- Newsline: Claude "Install as app", 24 Nov 2026, from Anthropic's own article (beta, all plans including Free, Mac and Windows, Share menu, permissions, online and signed in, usage counts, no review of apps). "Anthropic lists no country limits" is literal; it does not claim confirmed Australian availability beyond that.
- Looking Sideways: Sainsbury's AI self-checkout prompts (Retail Technology Innovation Hub, 26 Nov 2026). No Sainsbury's or SAI press release found, so the trade report is the source. 97% and two million transactions a day are as that report gave them. "Shoppers here have met cameras at the self-checkout too" is general knowledge about Australian supermarkets, kept loose. The picture shows a staff member near the tills; it is the article's own picture.
- Tool: Gemini Notebook's "make me a site" (Google blog, 16 Nov 2026; Digital Trends). Free with a personal Google account and 50 sources on free from Google's education page and 9to5Google (April 2026). Not in the last eight editions. Google appears in one section only; Anthropic in one (Newsline).
- Prompt of the Week ties to The Win: an interview prompt, one question at a time, playback before writing, [CHECK] for gaps, no invention, two fill-ins. Reviewed against notes/prompt-review-standards.md (role, reasons, one question at a time, guard against invention, defined output and stop).
- Odd One: Tidal deleting fully AI-made tracks from 9 Dec (Engadget, 24 Nov 2026): about 29 million, 43% of uploads over 90 days, 96% zero plays.
- Magnum: trend is AI Christmas snow globe and ornament pictures (many prompt guides; vendor-claimed trend, real seasonal demand). Made with openai/gpt-image-2.6/flare/text-to-image (newest image model on fal, published 4 Nov), then kling/v4/image-to-video, 5 s, 1080p, H.264 (avc1 checked), frames looked at. Mid-video the sand cloud briefly hides the ute and batsman; accepted, the still is the poster.
- ChatGPT for Accounting (Xero supported) was considered for Tool and dropped: no price or plan stated by OpenAI, and Xero describes the connection as read-only, which conflicts with "drafts invoices". Fyxer dropped: price shown without a currency. Amazon blocking Meta's Muse dropped as dated (September).
- WhatsApp line keeps the routine's fixed greeting ("Here's this week's This Week in AI"); the outside editor flagged "this week's" as relative time. Kept because the routine sets that line word for word.

## First screen: versions written and judged
Title: (1) "Claude now builds you a desktop app" (2) "She talked for an evening. Weeks of work, done." (3) "Weeks putting off one document. Done in one evening." Kept 3: a person like the reader and a result.
Opener: (1) Install as app (2) the full Win retold (3) a teaser of the Win ending "What finally got it done wasn't writing. It was talking." Kept 3, after the outside editor said 2 retold the story three times.
WhatsApp: (1) Claude app first (2) the Win first, then Claude (3) Win, Claude and the snow globe. Kept 3.

## Outside edit
Three rounds. Round 1: Win vague in places, Looking Sideways opened like a press release, Tidal headline 12 words, two loose Australia lines. Round 2: Win's key step vague, Looking Sideways lead repeated its headline. Round 3: the 97% figure had dropped out of the body (restored) and "soon" (changed). Round 3 also asked for a lead on The Win; not taken, because the routine sets The Win's layout as story paragraphs with do and take only.

## Stories read and not run
Anthropic IPO and its stock (money story). Claude and the Riemann Hypothesis proof, GPT-6 Astra quantum gravity preprint (no Monday action). Jensen Huang back at Nvidia, Nvidia selloff and export pause (politics and markets). OpenAI OpenWorks (US only). Microsoft 365 outage and Code Red (12 to 13 Nov, outside the window and close to last edition's failure angle). Character.AI chat sale, Treg People API (privacy, kept for a quieter week). GPT-6.2 billing correction. Claude Ship (developers). Meta Muse in Instagram DMs. Gemini 4 models, Inkling 2 Mini, llama.cpp 1.0 (model releases). MAGI-2 and Ideogram 4.6 (considered for the Magnum; fal-made globe chosen).

## Build command (for the Sunday run)
python3 tools/build_edition.py --edition build/2026-11-29/edition.json --magnum-video build/2026-11-29/the-magnum.mp4 --magnum-poster build/2026-11-29/the-magnum-still.png --illustration "The Newsline=build/2026-11-29/the-newsline.png" --illustration "Looking Sideways=build/2026-11-29/looking-sideways.jpg" --illustration "The Win=build/2026-11-29/the-win.jpg" --illustration "Tool of the Week=build/2026-11-29/tool-of-the-week.png" --repo /home/user/magnum-newsletter
