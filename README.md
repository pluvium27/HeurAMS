# HeurAMS - Heuristic Auxiliary Memorizing Scheduler

[中文](README_zh.md) | English

## Overview

HeurAMS "潜进" (Heuristic Auxiliary Memorizing Scheduler) is an auxiliary memorizing scheduler based on heuristic algorithms and cognitive science theories, designed to help users memorize and plan learning more efficiently.  
It is also an open, elegant, and extensible spaced repetition scheduler experiment platform, intended to help researchers conduct investigations, experiments, and research on cutting-edge memory algorithms more efficiently.

[Detailed Introduction](INTRODUCTION.md) | [Screenshots](SCREENSHOTS.md)

<p align="left">
<a href="https://github.com/pluvium27/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/GitHub-fafafa?style=for-the-badge&logo=github&logoColor=181717" alt="GitHub" /></a><a href="https://invent.kde.org/pluv/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/KDE_Invent-1D99F3?style=for-the-badge&logo=kde&logoColor=white" alt="KDE Invent" /></a><a href="https://gitee.com/pluv/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/Gitee-C71D23?style=for-the-badge&logo=gitee&logoColor=white" alt="Gitee" /></a><a href="https://git.pluv27.top/pluv/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/git.pluv27.top-609926?style=for-the-badge&logo=gitea&logoColor=white" alt="git.pluv27.top" /></a>
</p>

## Quick Start

### Installation

#### Install from Package Manager

HeurAMS (package name `heurams`) is in early development and not yet available on PyPI.  
However, you can install stable and development versions from the repository using pip, which requires a Python environment (Python 3.12.13 or later recommended).

Install from the stable `master` branch with optional dependencies for user experience (recommended):

```
pip install --upgrade 'heurams[basic] @ https://git.pluv27.top/pluv/HeurAMS/archive/master.zip'
```

Install from the more recent, roughly stable `dev` branch with optional dependencies (if you want cutting-edge improvements):

```
pip install --force-reinstall --no-deps 'heurams[basic] @ https://git.pluv27.top/pluv/HeurAMS/archive/dev.zip'
```

Install the general audio module for desktop computers (based on playsound3):\
(Not applicable for termux environments; termux has built-in audio support)

```
pip install --upgrade 'heurams[audio-playsound] @ https://git.pluv27.top/pluv/HeurAMS/archive/master.zip'
```

> You can also install from specific branches like `refactor/...` to test particular changes.

[Dependency Group Reference](INTRODUCTION.md#package-dependency-groups)

#### Install from Source

We provide two source installation methods: native Python and uv.  
See the [Contributing Guide - Setting up Development Environment](CONTRIBUTING.md#setting-up-development-environment) for details.

### Usage

Run `heurams` in your terminal, and you will see help information:

```plain
~ $ heurams
Usage: heurams [OPTIONS] COMMAND [ARGS]...

  HeurAMS 0.5.1 - Heuristic Auxiliary Memorizing Scheduler

Options:
  -v, --version  Show the version and exit.
  -h, --help     Show this message and exit.

Commands:
  help     Show this help message
  tui      Launch the built-in basic user interface (TUI)
  version  Print version information
```

Start the basic user interface by typing `heurams tui`:

```plain
~ $ heurams tui
Welcome to the basic user interface!
Loading config and context... Done! (2ms)
Loading UI framework... Done! (89ms)
Loading UI layout... Done! (56ms)
Component directory: <package directory>
Working directory: <working directory, ./data folder will be created here>
Pre-work total: 147ms

(Your terminal will now display the TUI)
```

Check the version with `heurams -v`:

```
~ $ heurams -v
HeurAMS 0.5.1 stable (fulcrum/支点), Linux
```

## Frequently Asked Questions (FAQ)

See [FAQ](FAQ.md).

## Project Architecture

See [Architecture Overview](ARCHITECTURE.md).

## Contributing

Contributions are welcome!  
See the [Contributing Guide](CONTRIBUTING.md).  
For AI-assisted development guidelines, see [AGENTS.md](AGENTS.md).

## Project Identity

HeurAMS project identity assets are located in `./src/heurams/assets/art/` directory:

<img src="src/heurams/assets/art/banner128-light.png" height="96px" title="Bitmap Banner (Opaque)">
<div style="display: flex; flex-wrap: wrap; gap: 5px;">
  <img src="src/heurams/assets/art/logo.svg" height="96px" title="Vector Icon">
  <img src="src/heurams/assets/art/logo-mono-light.svg" height="96px" title="Monochrome Light Vector Icon">
  <img src="src/heurams/assets/art/logo-mono-dark.svg" height="96px" title="Monochrome Dark Vector Icon">
</div>

Colors: `#1660A5 (Ocean Blue)` `#545F70 (Blue Gray)` `#FFFFFF (Monochrome Light Icon White)` `#1A1A1A (Monochrome Dark Icon Deep Black)` `#2f2f35 (Text Color)`.

## License

### Project

This project is open source under the AGPL-3.0 license, with an additional exemption clause for local API calls, making it more permissive than the standard AGPL-3.0.

See the [LICENSE](LICENSE) file in the root directory.

### Third-Party Code

The project embeds or directly uses the following third-party code or its derivatives (possibly with modifications) in `src/heurams/vendor/` or other locations:

#### SM.js

- Upstream version: commit `6e3bb4a` (upstream discontinued as of Feb 4, 2015)
- Usage: Rewritten from CoffeeScript to Python with indirect reference, maintaining the same mathematical principles; improved logic, performance, and standardized API
- Location: `src/heurams/kernel/algorithms/sm15m.py`
- Original project: [SM.js](https://github.com/slaypni/SM-15)
- Original copyright: Copyright (c) 2014 Kazuaki Tanida
- Original license: MIT License

This project benefits from their selfless and excellent work.
