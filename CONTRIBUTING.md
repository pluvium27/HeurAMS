# Contributing Guide & Development

Welcome and thank you for supporting this project!

Currently, the primary project repository server is the <a href="https://git.pluv27.top/pluv/HeurAMS" target="_blank" rel="noopener noreferrer">author's Gitea instance</a>, which manages synchronization, ensures availability, and accepts collaboration from multiple communities. Mirror syncs are set up on <a href="https://github.com/pluvium27/HeurAMS" target="_blank" rel="noopener noreferrer">GitHub</a>, <a href="https://invent.kde.org/pluv/HeurAMS" target="_blank" rel="noopener noreferrer">KDE Invent</a>, and <a href="https://gitee.com/pluv/HeurAMS" target="_blank" rel="noopener noreferrer">Gitee</a>.

This does not affect the project's acceptance of PRs from <a href="https://github.com/pluvium27/HeurAMS" target="_blank" rel="noopener noreferrer">GitHub</a>, <a href="https://invent.kde.org/pluv/HeurAMS" target="_blank" rel="noopener noreferrer">KDE Invent</a>, and <a href="https://gitee.com/pluv/HeurAMS" target="_blank" rel="noopener noreferrer">Gitee</a>. PRs accepted on GitHub, KDE Invent, and Gitee will retain contributor attribution and be synced back to all platforms as-is. Contributions on any platform are welcome.

> [!NOTE]
> We have begun development of a modern cross-platform frontend based on the KDE UI framework `Kirigami`, called "KiriMemo" (package name "org.kde.kirimemo"). Note that it is not a KDE project.\
> It directly reuses the Python kernel via `PyOtherSide`, providing a modern UI for Windows, Linux, macOS, Android, iOS, and Plasma Mobile.\
> If you are skilled in C++, QML, Qt, and KDE frameworks, you are welcome to join the KiriMemo project development.

## Development Conventions

Branch structure:

- `dev` branch (default branch): Mainline development branch. Used only for non-refactoring bug fixes and integration of feature branches. Pull requests are merged into this branch.
- `master` branch: Mainline stable version. `dev` is merged into `master` only when a stable version is released or a patch version is prepared.
- Feature and refactoring branches: Created from `dev`, named as `feature/description` or `fix/description` or `refactor/description` or `next/version`.
- Feature and refactoring branches should first be merged into `dev`, then into `master`.

Code formatting:

- Install tools:
  ```bash
  python -m pip install black autoflake mdformat
  ```
- For Python, use `black` and `autoflake`.\
  Commands:
  ```bash
  # black's multi-threading may have compatibility issues in some environments
  black . --workers=1
  ```
  ```bash
  # autoflake: note to exclude __init__.py
  autoflake --in-place --remove-all-unused-imports --recursive ./src/ --exclude __init__.py
  ```
- For Markdown, use `mdformat`.\
  Command:
  ```bash
  mdformat --number .
  ```
- For Textual CSS, use `prettier`.
- Formatting is not mandatory and can be consolidated into a single `style` commit, but code on `master` and `dev` branches should be kept clean for review.

Commit messages:

- Write clear commit messages in Simplified Chinese or English.
- Commit message format: Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. The `koji` tool is recommended.

Merge method:

- For consistency and traceability, Fast-forward merges have been prohibited since the repository was re-initialized after the v0.4.0 refactoring.
- You can set `git config merge.ff false`.

Commit author format:\
Due to the quirky git hook on KDE Invent infrastructure, the commit Author field must appear to be a real name (e.g., "Wang Zhiyu" instead of "wangzhiyu"; otherwise, KDE Invent's hook will reject the push).\
Therefore, please ensure your git configuration uses a proper name-like format (e.g., `git config user.name "Li Hua"`, i.e., must include a space). A real name is not required; the email field has no restrictions. You can also repeat a single name twice (e.g., "Thura Thura") to pass the check.

## Setting Up Development Environment

```bash
git clone https://git.pluv27.top/pluv/HeurAMS # Default branch is dev, no need to switch

cd HeurAMS

# If using uv (recommended)

python3 -m pip install uv

uv sync --all-extras # Sync development environment

uv run heurams

# If using native Python environment (not recommended, but retained for environments where uv and hardlinks are not supported, e.g., termux)

python3 -m pip install -e .[all] # Install dependencies and HeurAMS as a local package

python3 -m heurams # Verify installation

python3 -m heurams.interface # Launch TUI
```

## License & External References

Contributors retain copyright of their contributions and agree that their contributions will be released under the AGPL-3.0 license (including the additional local API call exemption clause).

Please note in your PR description if:

- You need to introduce other open-source vendor code
- You need to introduce other proprietary online services (e.g., edgetts in the current project)
- You need to upgrade a dependency or runtime environment version

## New User Interface Frontends

HeurAMS is designed as a frontend-independent library, meaning:

- Our built-in Textual TUI frontend is not the only available frontend.

- If you have developed a usable HeurAMS frontend (e.g., a not-yet-implemented Flutter frontend) and open-sourced it under AGPL-3.0/GPL-3.0, you can contact us to transfer it to the HeurAMS official repository for joint maintenance. You will retain your copyright and can lead development under that repository. :)

- You can also call HeurAMS as an independent process/service in your own projects. Per AGPL-3.0 and this project's additional license terms, if the call occurs on the same host and does not involve external network forwarding, it is exempt from specific obligations of the license and will not be "contaminated" by AGPL-3.0. To this end, we are improving the optional cross-process RPC module, which will become a cross-platform standard component of the "潜进" kernel.

- If you develop another piece of software through independent process/service invocation and open-source it but prefer not to use the AGPL-3.0/GPL-3.0 license, you can also contact us. We would be happy to add your project link to our friendly links.

## Non-Software Contributions

Even if you are not a software developer, you are welcome to contribute!

You can:

- Help create or proofread translations for the software interface and documentation in various languages
- Create open memory unit sets (including but not limited to text, images, and audio) for other users
- Improve the software documentation
- Answer questions from other users or share your experience
- Propose new ideas or report issues in the discussion area

You decide your role!
