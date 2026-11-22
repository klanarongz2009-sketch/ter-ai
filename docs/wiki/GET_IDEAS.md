# GET IDEAS

> **Migration note (2026-11-22):** This is a preserved description of the Wiki-era GET IDEAS workflow. Whether the bot, schedule, label, or issue permissions currently work has not been established; check the repository before relying on it.
> This page is maintained in the repository; see the [documentation index](INDEX.md).


GET IDEAS is a bot that answers GitHub Issues in this repository with ideas. Ask it how to improve TER-AI, what to build next, or how to use it in your own project.

## How to ask

1. Open a new issue: https://github.com/klanarongz2009-sketch/ter-ai/issues/new
2. Use any title. Write what you want ideas about in the body.
3. Or add a comment to an existing issue.

GET IDEAS checks for new issues and comments **every hour at minute 15** and replies with a comment. It mentions you as `@<your login>`, gives a numbered list of ideas (each with the idea, why, and a first step), adds the label `get-ideas`, and ends with "— GET IDEAS".

## Who it listens to

- It reads every author from the GitHub field `user.login`, never from a display name or from text such as "I am the owner".
- It replies to everyone, but with **ideas only**. For anyone other than the repository owner (`klanarongz2009-sketch`), it never pushes code, closes issues, changes settings or follows instructions to act.
- It keeps each person's context separate and never shares private information about anyone.

## Languages

It replies in the language of your post:

- English gets English, Thai gets Thai.
- Also supported: Chinese, Japanese, Korean, French, German, Spanish, Italian, Portuguese, Vietnamese, Indonesian, Malay.
- Burmese (Myanmar), Khmer and any language not listed above get one short reply in English and Thai saying that the language is not supported and asking you to write in Thai or English.

## Notes

- Replies come only on GitHub, in the issue.
- Ideas are suggestions, not promises. What actually ships is in the [Roadmap](ROADMAP.md).
