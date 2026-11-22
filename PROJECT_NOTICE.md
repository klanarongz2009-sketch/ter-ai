# Project notice

[ภาษาไทย](PROJECT_NOTICE.th.md)

This is an advance notice. TER-AI is an indie project run by one person, so it can stop with little or no warning.

Last updated: 2026-11-21 (latest release v0.18.3).

## Current state

- **Repository:** [klanarongz2009-sketch/ter-ai](https://github.com/klanarongz2009-sketch/ter-ai) (renamed from `terai-router`; old links redirect). The Python package is still named `terai-router`.
- **Tagentic1 (beta):** the TER-AI thinking + agentic model, running on local Gemma 4 E2B. It is beta and can be wrong.
- **Telegram bot [@Terai_F0_bot](https://t.me/Terai_F0_bot) (beta):** a Tagentic1 bot hosted by the maintainer. Public chats get a restricted mode: the shared knowledge file only, a few safe tools, rate limits, and no access to the maintainer's private files or to commands on the host machine. Anyone can also run their own bot with their own token ([setup guide](docs/TAGENTIC_TELEGRAM.md)).
- **Knowledge-inbox and fact checking:** facts sent with `/add` go to `Knowledge-inbox.md` first. Tagentic1 uses a fact only after it is checked against a real source (by a fact-checking AI agent run for the maintainer) and moved to `Knowledge.md`. Secrets, phone numbers, card numbers and email addresses are refused. Checking can be delayed while the maintainer is away or the agent's free credits run out.
- **Community and support bot:** questions, bug reports and ideas about the bot go to the [Tagentic telegram bot community](https://github.com/klanarongz2009-sketch/ter-ai/discussions/categories/tagentic-telegram-bot-community) on GitHub Discussions. The automated support bot Teemate may answer there first.
- **Deprecated components:** TTH (every version, TTH-MTL included) reaches end of service on 2026-11-30, and MuML (MuML 1.0 WA and MUML 1.0 HIQ), Temmo 1.0 and SANKPUP on 2027-01-10, because TER-AI is a Thai-language AI suite built around the Terai models and Tagentic. They may be removed from `main` on or after their date; pin a release tagged earlier to keep them. Anyone's repositories (individuals or companies, e.g. Google or OpenAI; no endorsement or partnership implied) may continue or fine-tune any TTH version from the last release that includes it (v0.18.3 today); the code stays MIT, the Wayu-Paxa-TTS-Edge and OmniVoice weights stay CC-BY-NC under their owners (commercial users need other weights or the owner's permission), and TER-AI does not maintain those forks ([deprecation notice](README.md#deprecation-notice)).
- **Response times:** the maintainer is a boarding-school student and is often away for long periods (see [Maintainer availability and urgent reports](#maintainer-availability-and-urgent-reports)). The hosted bot and the automated replies can stop at any time.

## Why the project may pause or close

- **Paused while the maintainer is at boarding school (personal reasons):** the maintainer is a boarding-school student and has been at school since around November 2, 2026. While at school, he is not allowed to use a phone or personal devices. Maintainer replies, updates and releases stop during that time and resume only when he is home. See [Maintainer availability and urgent reports](#maintainer-availability-and-urgent-reports).
- **Closed without a stated reason:** the project may close without an explanation.
- **A legal claim about models or data:** some optional models and data used by TER-AI have their own licenses (see the [license table](README.md#license) and [NOTICE](NOTICE)). If there is a legal claim about any of them, the affected part, or the whole project, may be taken down.
- **Generated music that sounds like a real song:** MUML 1.0 HIQ and MuML 1.0 WA make new music from a prompt, but output can happen to sound close to an existing song (melody, lyrics or style). If a rights holder files a claim, the music features, the demo, or the whole project may be taken down.
- **Other generated output causes a problem:** a TTH voice that sounds like a real person, a SANKPUP picture close to a protected logo or character, or a chat answer that is wrong or harmful may lead to a complaint and a takedown.
- **An upstream model or service changes:** a model's license may change, its weights may be removed from its host, or an online service (for example edge-tts or the Wikipedia API) may stop working. The parts that depend on it may break or be removed.
- **A platform action:** GitHub may disable the repository, the demo site or the wiki after a report (for example a DMCA notice) or a policy change.
- **A security problem:** if a serious vulnerability is found and cannot be fixed in time, or the maintainer cannot reach the project's systems to fix it, the affected part or the project may be pulled as soon as he has access.
- **No time or no resources:** school, health, cost (see [Cost and free services](#cost-and-free-services)) or loss of interest may stop the project.
- **Closed for good:** in the worst case, the project may be closed permanently.

## Maintainer availability and urgent reports

- **No access while at school:** the maintainer is a boarding-school student. While at school, he is not allowed to use a phone or personal devices, so he has no access to technology, the project's systems, its accounts or its contact channels. Access returns only when he is home.
- **Urgent reports wait:** during that time, a complaint, legal notice, security report, takedown request, platform report or any other urgent contact may not be read, answered or acted on until the maintainer is home. The delay can be long.
- **Urgent action comes first:** if a report needs urgent action, the maintainer may close, suspend or take down the affected part, or the whole project, as soon as he has access. This can happen without an in-depth review of the report and without a full explanation.
- **No guarantees:** there is no guaranteed response time and no guarantee of service continuity.
- **The bots are not the maintainer:** automated bots may still reply while the maintainer is away: GET IDEAS on GitHub Issues, and Teemate in the Tagentic telegram bot community on GitHub Discussions. The bots are not the maintainer. It does not receive or handle legal notices, security reports or takedown requests. A reply from a bot does not mean the maintainer has seen the issue or discussion.

## Cost and free services

TER-AI has no budget. Everything it uses is free today, so a change in any free service can stop the project.

- **Built with an AI agent on Sesame:** most of the work (code, model training, releases, the wiki and automatic issue replies) is done by an AI agent in the [Sesame](https://sesame.com) app. Sesame is free during its launch window and has said that a subscription is planned, with no plans or prices announced yet. Free use already has limits on agent work; when the limit is reached, work waits until it resets.
- **If Sesame starts charging, or free agent credits become too small:** training, new releases, demo updates and automatic issue replies may slow down or stop. If the free limit becomes too small to keep the project going, the project may close. The reason will be stated here, with a link to Sesame's announcement.
- **Other free services:** the repository, the demo site and the wiki are hosted free on GitHub (GitHub Pages), and optional model weights are downloaded from Hugging Face and other hosts. If their free terms change, the affected parts may stop working.
- **Sources:** [Sesame](https://sesame.com) for the app, its plans and its limits. Check there for the latest information, because plans may change after this notice was written.

## What happens when the project closes

Depending on the reason, some or all of these may happen:

- **The repository is archived (read-only) or deleted.** If it is deleted, `pip install git+https://github.com/klanarongz2009-sketch/ter-ai.git` stops working.
- **The hosted Telegram bot stops:** @Terai_F0_bot may go offline or be shut down, and the shared knowledge file may stop being updated.
- **The live demo goes offline:** https://klanarongz2009-sketch.github.io/ter-ai/ may stop working.
- **Releases and the wiki** may be removed or stop being updated.
- **Issues and pull requests are closed.** Automatic replies to issues and discussions stop.
- **No more updates or security fixes,** including for versions you already have.
- **A part may be removed on its own:** after a claim, only the affected feature (for example MUML 1.0 HIQ) may be taken out, and the rest may stay.
- **Model downloads may break:** commands that download weights (such as `terai muml --hiq --setup` or the first TTH run) depend on other hosts and may fail.

## What does not change

- Code you already downloaded keeps its license (MIT for TER-AI code; other parts as listed in [NOTICE](NOTICE)). A license that has been granted is not taken back by closing the project.
- Non-commercial and attribution terms of the optional models still apply to anything you made with them.
- You may fork the MIT code under its license. Parts with other licenses keep their own terms.

## What you should do

- Nothing here is a promise of support, updates, uptime or a response time.
- If you depend on TER-AI, keep your own copy of the version you use, and of any model weights you are allowed to keep.
- Check that music, voices and pictures you make do not copy someone else's work before you publish them.
- Before commercial use, read the [license table](README.md#license) again.

## How you will hear about it

When possible, a pause or closure will be announced at the top of the README and in this file. If the project closes without a stated reason, there may be no announcement. A takedown after an urgent report may happen before any announcement.
