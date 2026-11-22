# Router examples

From the repository root, use Python 3.11 or newer and install the core package with `pip install -e .`. The three examples run offline and need no optional dependencies.

## Basic routing

[Basic routing](basic.py) classifies five Thai messages, including ones with typos. Each line shows the original message, predicted intent, confidence score, and normalized text.

```sh
python examples/basic.py
```

```text
เส็ดหรือยัง              -> status    1.00  normalized: เสร็จหรือยัง
ช้วยบวก 15+27 หน้อย      -> calc      1.00  normalized: ช่วยบวก 15+27 หน้อย
```

## Chatbot routing

[Chatbot routing](bot_router.py) runs a scripted Thai conversation and sends confident predictions to intent-specific handlers. The `set_name` handler remembers a name for the current run, so `get_name` can answer a later message with it.

```sh
python examples/bot_router.py
```

```text
> ผมชือ่อะไร
  [get_name 1.00] โบกัส
```

## IoT command routing

[IoT command routing](iot_switch.py) prints the action it would take for each sample command. It maps `go_on`, `refuse`, `status`, and `help` to `CONFIRM`, `CANCEL`, `REPORT`, and `SHOW_HELP`, respectively. Other intents map to `IGNORE`.

```sh
python examples/iot_switch.py
```

```text
ทำเลย            go_on   1.00 -> CONFIRM
ไม่เอาดีกว่า     refuse  1.00 -> CANCEL
เส็ดยัง          status  1.00 -> REPORT
```
