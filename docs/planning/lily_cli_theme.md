
# Lily CLI Theme — “Iris Bloom” 🌙💜

> *“Simplicity is the ultimate sophistication.”* — Leonardo da Vinci

A cohesive purple-first theme for Lily’s command-line tools. Designed for legibility, vibe, and cross-platform consistency.

---

## Palette

| Token        | Name           |       Hex | Usage                          |
| ------------ | -------------- | --------: | ------------------------------ |
| `--iris-900` | Midnight Iris  | `#1A1026` | Base background (dark)         |
| `--iris-800` | Night Grape    | `#221433` | Alt background / panels        |
| `--iris-700` | Deep Amethyst  | `#3A1F5C` | Primary accents, borders       |
| `--iris-600` | Royal Wisteria | `#5B2E91` | Primary brand / headings       |
| `--iris-500` | Lily Purple    | `#7C3AED` | Primary highlight, cursor      |
| `--iris-400` | Orchid         | `#9D66FF` | Secondary highlight            |
| `--iris-300` | Lavender       | `#C0A8FF` | Muted accents                  |
| `--iris-200` | Lilac Mist     | `#E0D6FF` | Subtle dividers                |
| `--iris-100` | Moon Petal     | `#F3EFFF` | Light backgrounds (light mode) |

**Neutrals**

| Token       |       Hex | Usage                  |
| ----------- | --------: | ---------------------- |
| `--ink-900` | `#0E0E12` | Text on light          |
| `--ink-700` | `#B7B5C6` | Muted text on dark     |
| `--ink-100` | `#F7F7FA` | Text on dark (primary) |

**Semantic Signals**

| Role    |       Hex | Notes                           |
| ------- | --------: | ------------------------------- |
| Success | `#34D399` | Emerald (good contrast on dark) |
| Info    | `#38BDF8` | Sky blue                        |
| Warning | `#F59E0B` | Amber                           |
| Error   | `#EF4444` | Crimson                         |
| Pending | `#A78BFA` | Soft purple (queued/loading)    |

---

## Semantic Mapping

| Element         | Foreground   | Background   | Style   |
| --------------- | ------------ | ------------ | ------- |
| Prompt          | `--iris-400` | transparent  | bold    |
| Input text      | `--ink-100`  | transparent  | none    |
| Command (verb)  | `--iris-500` | transparent  | bold    |
| Flags / options | `--iris-300` | transparent  | none    |
| Path / file     | `#A0E7E5`    | transparent  | none    |
| Section header  | `--iris-600` | transparent  | bold    |
| Divider         | `--iris-200` | `--iris-800` | —       |
| Success msg     | `#34D399`    | transparent  | bold    |
| Info msg        | `#38BDF8`    | transparent  | none    |
| Warning msg     | `#F59E0B`    | transparent  | bold    |
| Error msg       | `#EF4444`    | transparent  | bold    |
| Hint / help     | `--ink-700`  | transparent  | italic  |
| Selection (TUI) | `--ink-900`  | `--iris-300` | reverse |
| Cursor          | `--iris-500` | —            | block   |

---

## ANSI / 16-Color Mapping

> Keep terminals that don’t support truecolor looking consistent.

| ANSI           | Purpose     | Color     |
| -------------- | ----------- | --------- |
| Black          | background  | `#1A1026` |
| Red            | error       | `#EF4444` |
| Green          | success     | `#34D399` |
| Yellow         | warning     | `#F59E0B` |
| Blue           | info        | `#38BDF8` |
| Magenta        | primary     | `#7C3AED` |
| Cyan           | path/links  | `#22D3EE` |
| White          | text        | `#F7F7FA` |
| Bright Magenta | emphasis    | `#9D66FF` |
| Bright White   | strong text | `#FFFFFF` |

---

## Rich (Python) — Theme Snippet

```python
from rich.theme import Theme

IRIS_RICH_THEME = Theme({
    "text": "#F7F7FA",
    "muted": "#B7B5C6",
    "prompt": "#9D66FF bold",
    "command": "#7C3AED bold",
    "flag": "#C0A8FF",
    "path": "#22D3EE",
    "rule.line": "#E0D6FF",
    "info": "#38BDF8",
    "success": "#34D399 bold",
    "warning": "#F59E0B bold",
    "error": "#EF4444 bold",
    "heading": "#5B2E91 bold",
})
```

Usage:

```python
from rich.console import Console
console = Console(theme=IRIS_RICH_THEME)
console.print("[heading]Lily[/heading] [muted]— ready[/muted]")
console.print("[prompt]lily >[/prompt] [command]run[/command] [flag]--fast[/flag] [path]project.petal[/path]")
```

---

## Typer — Styled Messages

```python
import typer
from rich.console import Console
from rich.theme import Theme

console = Console(theme=IRIS_RICH_THEME)

def info(msg: str): console.print(f"[info]ℹ {msg}[/info]")
def ok(msg: str): console.print(f"[success]✔ {msg}[/success]")
def warn(msg: str): console.print(f"[warning]▲ {msg}[/warning]")
def err(msg: str): console.print(f"[error]✖ {msg}[/error]")
```

---

## prompt\_toolkit — Style & Prompt

```python
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.completion import WordCompleter

IRIS_PT_STYLE = Style.from_dict({
    "prompt": "bold #9D66FF",
    "input": "#F7F7FA",
    "completion-menu.completion": "#C0A8FF",
    "completion-menu.completion.current": "bg:#C0A8FF #0E0E12",
    "scrollbar.background": "#221433",
    "scrollbar.button": "#9D66FF",
})

completer = WordCompleter(["run", "edit", "list", "help", "quit"], ignore_case=True)

while True:
    text = prompt([("class:prompt", "lily > ")], style=IRIS_PT_STYLE, completer=completer)
    if text.strip() == "quit":
        break
```

---

## Log Levels (Structured)

| Level   | Emoji | Color       | Example                  |
| ------- | ----- | ----------- | ------------------------ |
| DEBUG   | 🔍    | `--ink-700` | verbose execution detail |
| INFO    | ℹ️    | `#38BDF8`   | state changes, summaries |
| SUCCESS | ✔️    | `#34D399`   | completed steps          |
| WARNING | ▲     | `#F59E0B`   | recoverable issue        |
| ERROR   | ✖     | `#EF4444`   | failed step              |
| PENDING | ⏳     | `#A78BFA`   | waiting on I/O/agent     |

---

## Light Mode Variant (optional)

* Background: `#F3EFFF`
* Text: `#0E0E12`
* Primary: `#7C3AED`
* Muted: `#58546A`
* Dividers: `#E0D6FF`

> Keep signal colors the same; adjust contrasts only.

---

## Accessibility Notes

* Body text contrast on dark: `#F7F7FA` on `#1A1026` → WCAG AAA.
* Avoid long spans of `#C0A8FF` on dark for body copy (use for accents only).
* Use bold for headings and state labels to improve scannability.
* For users with blue-purple color confusion, pair **icons** with color (see log level emojis).

---

## Sample UI Sketch (mental model)

```
┌ Lily — Iris Bloom ─────────────────────────────────────────────┐
│ lily > run research.petal --fast                              │
│ ✔ Completed: Vectorize dataset (3.2s)                         │
│ ▲ Warning: 2 files skipped (unsupported)                      │
│ ℹ Output at /output/research_2025-08-12/                      │
└────────────────────────────────────────────────────────────────┘
```

---

## File/Token Names for Docs & Code

* Theme codename: **Iris Bloom**
* Primary token prefix: `iris-` (purples), `ink-` (neutrals)
* Python constant: `IRIS_RICH_THEME`, `IRIS_PT_STYLE`
* Environment toggle: `LILY_THEME=iris-bloom`
