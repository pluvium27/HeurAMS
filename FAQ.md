# Frequently Asked Questions

## What is a terminal emulator?

A terminal emulator is an application that simulates and uses a terminal within a graphical desktop environment, e.g., KDE Konsole, GNOME Terminal, Windows Terminal, iTerm2, etc.

The old, modest little black window on older Windows (conhost.exe) is also a terminal emulator, but it has poor support for this software's basic user interface (and all modern terminal applications). We recommend using WezTerm (supports sixel) or Windows Terminal (does not support sixel) on Windows.

## Does the software support mobile devices?

The basic user interface (Textual TUI) works well in Android Termux.

Additionally, the KiriMemo frontend under development is based on the KDE Kirigami framework and will natively support Android and iOS.

## What is the difference between HeurAMS and Anki?

At a high level:

| Aspect | HeurAMS | Anki |
|--------|---------|------|
| Data format | Text files (TOML/JSON), human-readable | Proprietary compressed format with SQLite and resources (.apkg) |
| Review modes | Multi-phase flow + multiple puzzle types | Single/double-sided flashcards |
| Algorithm system | Modular, pluggable, multiple algorithm options | Built-in SM-2 / FSRS |
| Plugin ecosystem | Smaller, manifests as "capability extensions" like new algorithms or services | Larger, but uses unrestricted "monkey patching" |
| User base | Small | Large |
| Existing resource richness | Low | High |
| AI-assisted unit set/deck creation | Natively supported | Difficult |
| License | AGPL-3.0 with additional exemption clause | AGPL-3.0 |

## Is the software free?

Yes, completely free and open source. You can use all features without paying anything.

## How do I use this dark-looking interface?

First, if you just want a light color scheme, press the `d` key or click the "d theme" button to switch to a light interface. :)

Thanks to Microsoft's decades of "the command line is outdated" education, and the poor experience of `conhost.exe` and `cmd.exe`, it's completely normal to feel uncomfortable with a terminal user interface.

But in reality, even though it looks like an old computer screen, Textual and terminal standards are more modern than you might think.

### You can use the mouse

Modern terminal emulators (such as Windows Terminal, Konsole, iTerm2, WezTerm, etc.) support a feature called "Mouse Tracking". When Textual starts, it sends special instructions to the terminal to report mouse events.

So contrary to what you might expect, you can actually click buttons with your mouse, just like in regular software.

### You can also use the keyboard

- `Tab` key switches focus between different areas
- `Arrow keys` move up and down in lists
- `Enter` confirms a selection
- `q` goes back
- Key hints are displayed on screen, e.g., `[n] Navigator` means pressing `n` opens the navigator

### Touchscreen also works

On tablets or phones in Termux, you can touch or swipe to operate.

## How do I start the software?

First, ensure Python (3.12.13 recommended) is installed on your system along with the required HeurAMS components.

### Windows

Open "Command Prompt" or "PowerShell", enter the following command and press Enter, or save it as a shortcut:

```
python -m heurams.interface
```

### macOS

Open the "Terminal" application and enter the above command.

### Linux

Open your terminal emulator (usually Ctrl + Alt + T) and enter the above command.

If you find typing the command every time too cumbersome, you can create a desktop shortcut or script file. See online tutorials for details.

## How do I exit the software?

Press the `q` key to return to the main screen, then exit.

Your learning progress is saved automatically and will not be lost.

## Images are very pixelated and blurry, what should I do?

This means the image is being displayed in Halfcell compatibility mode.

The terminal emulator needs to support the sixel image protocol for high-quality image display. For terminals that don't support it, the software can only display images in low-quality compatibility mode.

- WezTerm (all major OS): Supported
- KDE Konsole: Supported
- GNOME Terminal: Not supported
- iTerm2 (macOS): Supported
- Windows Terminal: Not supported
- mintty (Windows): Supported

If your terminal doesn't support images, other software features are unaffected — only images in memorization content won't be displayed.

## Chinese characters display as garbled text or boxes?

This means your terminal's Chinese font is not set correctly. Please check:

1. You are not using terminals like getty or xterm that explicitly do not support non-ASCII fonts
2. In the terminal settings, choose a font that supports Chinese, such as "Noto Sans SC", "Microsoft YaHei", "Source Han Sans"
3. Ensure the terminal's character encoding is set to UTF-8 (usually the default)

## Where is my data stored? Will it be lost?

Data is stored in the `data/` folder under the software installation directory:

- You can open and modify files directly with a text editor
- Copy the `data/` folder to a USB drive or cloud storage for backup (regular backups recommended)
- Even if the software is uninstalled, as long as you keep the `data/` folder, all learning records will be preserved when you reinstall and copy it back

## How do I share my unit sets with friends?

Find the corresponding folder under `data/repo/`, copy the entire folder, and send it to your friend. They can place it in their own `data/repo/` directory to use it.

You can also export as a single text file or compressed archive and share via messaging apps, email, etc.

## I can't copy/paste content?

Generally, in a terminal:

- Copy: Ctrl+Shift+C
- Paste: Ctrl+Shift+V

This differs from regular software habits (because Ctrl+C means "interrupt process" in terminal semantics), but you'll get used to it quickly.

## The font is too small/large?

Adjust the "font size" option in your terminal emulator settings.

The software follows the terminal's font settings.

## Why does my interface look different from the screenshots?

The screenshots were taken using Konsole on KDE Plasma desktop, 80x25 character size, with Cascadia Code and Noto Sans SC fonts.

If your terminal size is larger, the interface will have more room. Using different fonts or operating systems may result in slight visual differences.

Functionality is identical.

## What do the ratings (1-5) mean? How should I rate?

We should note that we strongly discourage the Anki-like approach of having users directly self-rate their performance (implemented as `basic_puzzle` in our program, used primarily for algorithm testing).

We believe this approach is highly subjective and requires you to think about "What score am I?", "Am I being too optimistic?", "Am I scoring too low?", "What if I rate incorrectly?" — a series of questions that interrupt the memorization process and cause anxiety. This essentially shifts responsibility to the user and contradicts cognitive science principles.

Moreover, this approach is detrimental to academic research and experimentation, as user self-rated data is unreliable.

Therefore, HeurAMS frontends have built-in automatic rating systems based on user behavior analysis, i.e., "puzzles".

It automatically rates you based on the difficulty of the question and your answering behavior (including but not limited to correctness, number of operations undone, effective answering time).

However, if you or a unit set chooses to use `basic_puzzle`, or if you plan to implement your own automatic rating system, the meaning of scores is as follows:

| Score | Meaning | Description |
|-------|---------|-------------|
| 1 | Completely forgotten | Couldn't recall at all, as if never learned |
| 2 | Vague | Seems familiar, but couldn't answer |
| 3 | Some impression | Recalled after thinking for a while, not very certain |
| 4 | Relatively smooth | Could answer, but hesitated slightly |
| 5 | Very easy | Immediately recalled, no effort |

- Scoring **1-2**: The software considers you haven't mastered it and will schedule another review soon
- Scoring **3**: Normal mastery, review at the planned interval
- Scoring **4-5**: Well mastered, the next review interval will be extended

We suggest you don't overthink it, just score based on your first instinct — the software will automatically adjust the review pace based on your ratings.

Of course, we still recommend avoiding this approach and using other puzzle types for evaluation when possible.

You might think this method allows users to directly "intervene" with the algorithm, similar to Baicizhan's "斩" (chop) feature for skipping familiar content. In reality, you don't need to do that: we have built-in "quick pass/correct response" functionality, equivalent to directly selecting "5".

## Do I need to open the software every day? What if I don't study?

In theory, you don't need to open it every day. The software automatically records when each knowledge point is due for review next.

However, it is recommended to open the software daily to check your status.

Even if you skip studying for days or weeks:

- Knowledge points you've already learned won't disappear — they'll just need a few more reviews next time
- Learning records are safely stored in the `data/` folder and won't be lost

For best results, try to follow the software's review reminders; but it's okay to skip a few days when you're busy.

## Can I study multiple subjects simultaneously?

Yes.

Each subject or course can be made into an independent "unit set".

## I changed computers. How do I migrate data?

1. On the old computer, copy the entire `data/` folder to a USB drive or cloud storage
2. Install HeurAMS on the new computer
3. Overwrite the new computer's `data/` folder with the one from the USB drive

All learning records, configurations, and unit sets are fully migrated.

## I don't understand some terminology

| Term | Meaning |
|------|---------|
| **Unit Set** | Like a "book" or "course", containing a series of knowledge points |
| **Puzzle** | A question type to test you (MCQ, Cloze, etc.) |
| **Algorithm** | The "intelligent scheduler" that decides when to review which knowledge point |
| **Review Queue** | The list of knowledge points due for review today |
| **Activation** | Starting to learn a knowledge point for the first time |
| **Due** | A knowledge point is due for review |

## The software is stuck/unresponsive?

1. First, wait a moment
2. If that doesn't work, close the terminal window directly
3. Reopen the software
4. If you have time, please report the issue. We apologize for the inconvenience.

## Will using both Anki and HeurAMS cause conflicts?

No.

They are independent software programs with no data interference. You can gradually migrate content to HeurAMS, or use both together.

## Do I need to install Python?

Yes. HeurAMS is a Python-based software.

- Windows/macOS: Download and install from python.org
- Linux: Python is usually pre-installed
- Android: Install the Termux app, then install Python within Termux (run `pkg in python`)

If you see an error like "python is not recognized as an internal or external command", Python is not properly installed or added to your system PATH. Search for "Python installation tutorial" and follow the steps.

The recommended Python version for HeurAMS is 3.12.13.

## Is the software safe? Could it contain viruses?

HeurAMS is open source software. All code is publicly available for inspection and contains no viruses or backdoors.

It only reads and writes to its own `data/` folder and will not touch other files on your computer.

## The software shows an error with a lot of text I don't understand?

1. Copy the error message
2. First check if this page covers your issue
3. If not, upload it along with the software logs to issues, and we will handle it as soon as possible

## Can I pause mid-review? Will it restart from the beginning?

There is currently no save-state functionality, but we will add it soon.

## How do I see how much I've learned? Are there statistics?

The dashboard interface displays statistical information.

You can return to the dashboard anytime via the navigator.

## I feel the review is too fast/slow. Can I adjust it?

Yes. You can change the review pace by switching algorithms, adjusting algorithm parameters, or changing the number of memory units.

Relevant settings can be found in the settings interface.

## Can I change the interface color/theme?

Yes. The Textual framework provides various themes.

## I accidentally deleted something. Can I recover it?

This depends on whether your system has a recycle bin enabled. The software itself does not have an auto-backup function.

## Can I carry the software on a USB drive?

Yes. Copy the entire HeurAMS folder to a USB drive, install Python on any computer, and run it. Learning data in the `data/` directory will also be carried along.

## How do I turn off voice reading?

Find the TTS-related option in the settings interface and disable it.

## Where can I download unit sets made by others?

Currently, there is no official unit set marketplace.

However, as the community grows, users may share unit sets in the future. You can also share unit sets with friends.

## Can I export learning content for printing?

Yes.

The software supports exporting unit sets as a single text file, which you can open and print with any text editor. You can also copy content directly into software like Word.

## I want to start over from scratch. How do I reset?

Delete the `algodata.json` file in the corresponding unit set folder under `data/repo/` to reset all learning progress.

## How do I create my own unit set?

Create a new folder under `data/repo/` with the following files:

```
data/repo/my_pack/
├── manifest.toml    # Meta info: title, author, etc.
├── typedef.toml     # Common field definitions and puzzle configuration
├── payload.toml     # Memory item content
├── algodata.json    # Algorithm state data (can be empty)
└── schedule.toml    # Review strategy configuration
```

You can also use the tools we provide to convert from CSV format, or use AI tools to generate unit sets.

## How do I switch algorithms?

Detailed instructions are available in the settings interface.

## How do I import from Anki?

There is currently no migration tool, as the design philosophies of the two software programs differ.

But keep an eye on the HeurStudio project — it will fundamentally solve content creation and migration issues. :)

## Why not Flutter?

Flutter is an excellent framework for building cross-platform graphical interfaces. One of HeurAMS's design goals is to keep the core library independent of any specific frontend.

However, Flutter is not as good as PyOtherSide when it comes to "integrating Python" — it can only communicate with the library through RPC standard components. Additionally, Flutter's desktop multi-window support has not been officially and stably supported, so we temporarily abandoned Flutter in favor of Kirigami.

Currently, we have prioritized the development of a Textual-based TUI frontend and a Kirigami-based native frontend. However, this does not preclude the possibility of a Flutter or other framework frontend in the future.

If you are interested in developing a Flutter frontend, please refer to the [Contributing Guide](CONTRIBUTING.md#new-user-interface-frontends).

## Does the software need internet access?

Core review functionality works completely offline. The following features require internet:

- Edge TTS provider for Text-to-Speech
- LLM providers (e.g., OpenAI compatible API)
- Downloading unit sets from remote repositories

## What is the "local API call exemption" in the license?

In short, if you use HeurAMS in your own program through local inter-process API communication (such as RPC calls on the same host) without network forwarding, your program is not bound by the AGPL-3.0 license.

This additional clause is designed to encourage the development of third-party frontends and tools.

Therefore, HeurAMS's license is effectively more permissive than the original AGPL-3.0.

## What is the difference between HeurAMS and Baicizhan?

At a high level:

| Aspect | HeurAMS | Baicizhan |
|--------|---------|-----------|
| Usage scenario | Computer/Terminal | Mobile App |
| Learning content | Any knowledge, unlimited languages and subjects | English vocabulary |
| Memory strategy | Multiple algorithms, customizable review flow | Fixed algorithm, not adjustable |
| Quiz methods | Multiple puzzle types: MCQ, Cloze, Recognition | Picture-word matching, audio-meaning selection, etc. |
| Content creation | Self-created or imported, completely free | Official word books only |
| Cost | Completely free, no in-app purchases | Free memorization + paid courses |
| Data ownership | Data in your hands, text files | Data cannot be extracted |
| Offline use | Core functionality fully offline | Some features require internet |
| Learning statistics | Basic statistics | Check-in/Leaderboard/Social |

## Baicizhan has picture association memory. Does HeurAMS have it too?

Yes.

If your terminal supports image display (such as Konsole or WezTerm), unit sets can include images that will be displayed during review.

However, you need to add images to the unit set yourself.

## Baicizhan has check-ins and leaderboards. Does HeurAMS have them?

Currently no.

HeurAMS does not have check-ins, leaderboards, or social features, and does not collect your learning data.

## Baicizhan has ready-made word books. Where can I find content for HeurAMS?

Baicizhan's courses are officially made. HeurAMS content needs to be created by yourself or obtained from the community.

See "How do I create my own unit set?" for details.

## Baicizhan is convenient to use on mobile. Can HeurAMS be used on mobile?

Yes, but at this stage it requires some setup.

Android users can install Termux to run HeurAMS's basic user interface.

Additionally, the KiriMemo frontend under development will natively support Android and iOS, requiring no setup from users.

## Baicizhan helps with vocabulary. What else can HeurAMS be used for?

Any knowledge that requires memorization: foreign language vocabulary, medical terminology, legal texts, historical dates, chemical equations, programming syntax, musical notation...

Unit set content is entirely defined by you.

## Baicizhan is effective for learning English. Will HeurAMS be less effective?

Considering that Baicizhan's algorithms and vocabulary database are effectively closed-source, we have no way of knowing the algorithm source.

However, HeurAMS's architecture design ensures that once a unit set is created, it can be at least as effective as Baicizhan — or even better.

HeurAMS's spaced repetition algorithms are based on the same cognitive science principles, and the algorithms are transparent and adjustable, allowing you to freely choose the scheduling strategy that best suits you.

## How do I participate in the project?

See the [Contributing Guide](CONTRIBUTING.md).

Even if you are not a developer, you can participate by writing documentation, creating memory unit sets, translating the interface, answering questions, and more.
