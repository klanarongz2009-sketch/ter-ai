# Tagentic1 on Telegram: set up your own bot

Tagentic1 is a **beta** (release candidate in v0.18.0-rc1). `terai tagentic telegram` runs it as a Telegram bot with a bot token that you create. Everything runs on your own machine; there is no hosted service and nothing to pay.

Community: the **Tagentic telegram bot community** section on GitHub Discussions, with four categories:

- [Tagentic telegram bot community](https://github.com/klanarongz2009-sketch/ter-ai/discussions/categories/tagentic-telegram-bot-community): general talk and show and tell; start here if unsure.
- [Tagentic bot Q&A](https://github.com/klanarongz2009-sketch/ter-ai/discussions/categories/tagentic-bot-q-a): how to install, set up and use the bot. Mark the reply that solved it as the answer.
- [Tagentic bot bug reports](https://github.com/klanarongz2009-sketch/ter-ai/discussions/categories/tagentic-bot-bug-reports): errors and problems. The form asks for the version, OS, command and error.
- [Tagentic bot ideas](https://github.com/klanarongz2009-sketch/ter-ai/discussions/categories/tagentic-bot-ideas): features and improvements.

Never post your bot token or chat IDs there. Replies may come from Teemate, an automated support bot; it is not the maintainer (see [PROJECT_NOTICE](../PROJECT_NOTICE.md)).

## What you need

- TER-AI installed with the `llm` extra (`pip install "terai-router[llm] @ git+https://github.com/klanarongz2009-sketch/ter-ai.git@v0.18.0-rc1"`) and the Gemma 4 E2B weights (`terai tagentic --setup`). Check that `terai tagentic "hello"` answers before you connect Telegram.
- A Telegram account to create the bot.
- A machine that stays on. On an 8-vCPU machine without a GPU, the first reply after a model load takes about 1 to 3 minutes; later replies are faster.

## 1. Create a bot with BotFather

1. In Telegram, open [@BotFather](https://t.me/BotFather) and send `/newbot`.
2. Choose a display name and a username that ends in `bot`.
3. BotFather replies with a token like `123456789:AA...`. Treat it like a password: anyone with it controls your bot.

## 2. Store the token

Use an environment variable or a file that only you can read. Do not put the token in a repository, a chat or a file name.

```sh
export TAGENTIC_TG_TOKEN='123456789:AA...'
# or
mkdir -p ~/.config/tagentic
printf '%s' '123456789:AA...' > ~/.config/tagentic/telegram_token
chmod 600 ~/.config/tagentic/telegram_token
```

The bridge never prints or logs the token. `TAGENTIC_TG_TOKEN` wins over `token_file`.

Check it:

```sh
terai tagentic telegram --token-file ~/.config/tagentic/telegram_token --check
# ok: @your_bot (id 123456789)
```

## 3. Find your chat id (owner)

Owner chats get the full model. To find your id, start the bot once without `--owner`, send it `/start`, and read your id from the bot log line `start chat=<id> ...`. Then stop it and add `--owner <id>` (or `"owners"` in the config).

## 4. Run it

```sh
terai tagentic telegram --token-file ~/.config/tagentic/telegram_token --owner 123456789
```

Or with a config file (print a starter with `terai tagentic telegram --example-config`):

```json
{
  "token_file": "~/.config/tagentic/telegram_token",
  "owners": [123456789],
  "memory_dir": "~/.terai/tagentic",
  "workspace": "~/tagentic-workspace",
  "state_dir": "~/.terai/tagentic/telegram",
  "max_queue": 3,
  "turn_timeout": 900,
  "public": {"open": true, "msgs_per_hour": 6, "adds_per_hour": 10, "max_public_queue": 2}
}
```

```sh
terai tagentic telegram --config ~/.config/tagentic/telegram.json
```

The log prints `bridge up as @your_bot ...` when it is ready. The example ids above are placeholders; use your own.

To keep it running after a reboot, run the same command from your service manager (for example a systemd user service).

## Owner mode and public mode

The mode is decided in code, not in the prompt.

| | Owner chat | Public chat (everyone else, every group) |
|---|---|---|
| Who | private chat whose id is in `owners` or in `<state_dir>/allowlist.json` | any other private chat, and all groups |
| Memory | `User.md`, `Memory.md`, `Knowledge.md` | `Knowledge.md` only |
| Tools | all tools; writes, edits, code and shell runs wait for **Allow** / **Deny** | calculator, datetime, units, add_knowledge (nothing that needs approval) |
| Sessions | `<memory_dir>/sessions/tg-<chat id>.json` | `<state_dir>/public/sessions/tgp-<chat id>.json` |
| Limits | up to `max_queue` waiting messages, goes first in the queue | `msgs_per_hour` and `adds_per_hour` per chat, `max_public_queue` public turns waiting in total, one message at a time per chat |

In groups the bot only answers commands, messages that mention it, and replies to its own messages.

The `public` block is read again on every message, so you can change limits without a restart. Set `"open": false` to close the bot to everyone except owners; private chats that try are recorded in `<state_dir>/pending.json`, and you can let one in by adding its id to `allowlist.json`:

```json
{"chat_ids": [123456789]}
```

## Commands

- `/start`, `/help`: how to use the bot, with links to this page and the community.
- `/add <information>`: send one fact to the knowledge inbox (`Knowledge-inbox.md`). Secrets, phone numbers, card numbers, email addresses and texts over 1000 characters are refused. Tagentic1 uses a fact only after someone checks it against a real source and moves it to `Knowledge.md` (`python -m terai_router.tagentic.knowledge --verify` / `--reject`).
- `/reset`: delete this chat's session and start again.
- `/approve`, `/deny` (owner only): answer a permission request; the buttons under the message do the same.

## What the bot says

Every text the bot writes itself is English and starts with `[System]`, for example `[System] In the queue (position 2). Replies can take a few minutes.` Text the model writes (its short thinking lines, tool results and answer) is sent as the model wrote it, in any language, with no header and no timing line. A permission request ends with `[System] Permission needed: <action>`.

## Privacy

- The log keeps chat ids, message sizes and timings. It does not keep the text of messages.
- Public chats never load `User.md` or `Memory.md`.
- Everything stays on your machine. Telegram itself sees the messages, as with any Telegram bot.

## Troubleshooting

- `no bot token`: set `TAGENTIC_TG_TOKEN` or pass `--token-file`.
- `getMe: 401 Unauthorized`: the token is wrong or was revoked in BotFather.
- `FROZEN_METHOD_INVALID`: Telegram has frozen the bot. The bridge cannot fix this; appeal to Telegram or create a new bot.
- `getUpdates: 409 Conflict`: another program is polling the same bot. Stop it, or remove its webhook.
- Very slow first reply: the model is loading. Later turns reuse the loaded model through the local server.
- Something else: ask in [Tagentic bot Q&A](https://github.com/klanarongz2009-sketch/ter-ai/discussions/categories/tagentic-bot-q-a) or report it in [Tagentic bot bug reports](https://github.com/klanarongz2009-sketch/ter-ai/discussions/categories/tagentic-bot-bug-reports), without your token or chat IDs.

## License

`src/terai_router/tagentic/telegram.py` and its tests are new files under the TER-AI License 1.0 (`SPDX-License-Identifier: LicenseRef-TER-AI-1.0`, see [LICENSE-TER-AI.md](../LICENSE-TER-AI.md)). Free to use, including commercially and for AI training, with credit to "TER-AI (klanarongz2009-sketch)".
