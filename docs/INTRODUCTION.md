## Features

### Spaced Repetition Scheduler

> Numerous publications have extensively discussed the effects of different repetition intervals on learning outcomes. In particular, the spacing effect is considered a universal phenomenon. The spacing effect refers to the fact that learning performance improves when repetitions are distributed/spaced rather than massed. Therefore, it has been proposed that the optimal repetition interval for learning is the **longest interval that does not lead to forgetting**.

- The software works out of the box, using the default `SM-2` algorithm for learning without additional configuration
- The algorithm module is a first-class citizen in the kernel (`heurams.kernel`), which natively supports pluggable algorithms of various types
- No complicated plugins required — algorithms can be quickly switched and tuned per unit set, enabling researchers to easily modify algorithm modules for convenient research and testing
- Defaults to the `SM-2` simple spaced repetition algorithm, also used as the default flashcard scheduler for Anki
- Also includes `NSP-0` non-spaced filtering algorithm for rapid content screening, `FSRS` advanced spaced repetition algorithm as a more efficient scheduler, and `SM-15M` (ported from sm.js project) complex spaced repetition algorithm (reverse-engineered)
- Algorithm modules can tag memorization items, dynamically plan memory interval schedules for each unit, and track memory feedback data to optimize long-term retention and stability
- Thanks to the modular architecture and unit set structure design, the same unit set can coexist and interoperate with any algorithm — extremely friendly for researchers and users exploring/experimenting with efficient methods

### Multimodal Learning Process

Unlike Anki's SQLite `.apkg` packages, we insist on using human-readable folder-organized unit sets, which brings several benefits:

- **Human-readable**: You can freely modify memorization payload data with any tool, even a simple text editor, without opening the software
- **Metadata configuration**: Extremely flexible configuration — you can freely combine, remix, or even create new content
- **Quiz, algorithm, and knowledge isolation**: A piece of knowledge is no longer a single flashcard; it can not only be scheduled with different algorithms but also tested with multiple parallel puzzle types, greatly enhancing learning effectiveness and richness. As a learner, you don't need to worry about complexity — just download a unit set from the cloud and use these features out of the box!
- **Multimodal learning**
  - The software integrates Text-to-Speech (TTS), audio, and LLM modules — all pluggable, extensible, and driver-switchable, creating great content richness
  - Built-in puzzle types include Multiple Choice Questions (MCQ), Cloze Deletion, and Recognition, all applicable to the same unit or selectively enabled
  - Natively supports dynamic content generation with macro-driven template systems that generate knowledge point explanations based on context or even LLMs
  - In the era when SuperMemo series dominated spaced repetition research, Wozniak already stated, "If you cannot understand knowledge, you don't need to memorize it." Today, we still believe understanding is the foundation of memorization
- **Cloud sync and sharing optimized**:
  - Since memory data and unit set files are text files, fast incremental sync is possible without uploading all files, and the design natively supports version control
  - If you want to share a single file, the software supports exporting as a compressed package or merging into a single text file for sharing on platforms like pastebin
- **Performance**: Thanks to the modern, chunked file organization structure, HeurAMS achieves agile and low-footprint user experience using only Python while maintaining high flexibility
- **AI-assisted friendly**: Imagine you have some `.apkg` decks or a large amount of textbook content — you can conveniently and efficiently use AI tools to create HeurAMS-compatible unit sets

### Built-in Practical User Interface

Although not the only frontend, the responsive Textual framework-based built-in terminal user interface has unique advantages in many scenarios:

- Cross-platform, with touch/mouse/keyboard multi-operation modes
- Compatible with almost all modern terminal emulators
- High-quality image display on terminal emulators that [support the sixel protocol](https://www.arewesixelyet.com/)
- Low-resolution compatibility display mode for terminals that don't support sixel
- Deployable as a service via textual-web, usable from any browser
- Clean, intuitive, keyboard-friendly, full-featured, and efficient UI design
- Easy to embed: can run in getty/kmscon without any desktop graphics service
- Low resource footprint, smooth operation
- Convenient for testing and debugging the library

View [Screenshots](SCREENSHOTS.md).

## Package Dependency Groups

Since some dependencies are only needed by a few features, we split optional dependencies into fine-grained groups. Here are the dependency groups:

| Dependency Group | Included Modules | Description |
|------------------|------------------|-------------|
| Build System | hatchling | Build-time installation |
| Minimal | tabulate, toml, transitions, click | Core driver libraries, always required |
| interface | textual | Basic user interface dependencies |
| algo-fsrs | fsrs | FSRS algorithm module |
| tts-edgetts | edge-tts | Microsoft Text-to-Speech |
| llm | llms-py | API calls |
| audio-playsound | playsound3 | General audio module |
| dev | zmq, pytest, pytest-cov | Development, debugging, and testing tools |
| basic | [tts-edgetts], [llm], [algo-fsrs | Lighter dependency group for user experience (recommended) |
| all | All of the above | Complete installation group |

## About This Repository

This repository is the Python implementation of the HeurAMS core library.  
It contains data models and framework, and includes a built-in frontend based on the Textual framework (interface submodule).  
Besides learning through the built-in frontend, developers can import the `heurams` library in a Python environment or communicate with `heurams` library instances via `RPC`, using the framework to build other auxiliary memory frontends or applications.

All repositories of the project group:

| Project Name | Status | Description | Package Name | Tech Stack | Target Platform |
| :--- | :--- | :--- | :--- | :--- | :--- |
| HeurAMS | In Development<br/>Prototype Usable | General core library with basic UI | `heurams` | Python | Standard Python Environment |
| KiriMemo | In Development<br/>Prototype Usable | Modern cross-platform frontend based on KDE technology | `org.kde.kirimemo` | C++, Qt6, Kirigami, PyOtherSide | Desktop & Mobile |
| ArkMemo | In Development | Modern cross-platform frontend based on ArkUI | `top.pluv27.arkmemo` | ArkTS, ArkUI | Mobile Devices |
| HeurStudio | Planned | AI-assisted single-unit set advanced creation and editing tool | `top.pluv27.heurstudio` | C++, Qt6, Kirigami, PyOtherSide | Desktop |
| HeurSync | In Development | User data sync server<br/>with Web frontend and leaderboard | `heursync` | Go, SQL | Web & Server |
| HeurRepo | In Development | Unit set document source server<br/>and sharing platform | `heurrepo` | Go, SQL | Web & Server |

Although the last three might sound a bit ambitious, our roadmap is clear.
