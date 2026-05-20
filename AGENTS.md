# AI Coding Assistant Guide

This document provides guidance for AI tools and developers using AI assistance to contribute code to the HeurAMS project. Generally, this file will be automatically loaded into the context of various AI tools.

AI tools should read this `/AGENTS.md` file in its entirety.

## Reference Documents

When assisting with HeurAMS development, AI tools should follow standard development practices and procedures. They should automatically check, or check upon user issuing an "init/初始化" command:

- [Contributing Guide](/CONTRIBUTING.md)
- [README](/README.md)
- [Architecture Overview](/docs/ARCHITECTURE.md)

## Prohibited Actions

1. AI must not automatically generate PR or patch files
2. AI must not modify existing code without human confirmation
3. AI must not generate formatted files without using formatting tools
4. AI must not fix any "bugs" without human confirmation
5. AI must not engage in any "cowboy coding" that bypasses project design principles or creates separate libraries
6. AI must not directly operate pip, uv, apt, or other tools to modify external dependencies or tools — human developers should handle dependencies themselves
7. AI must not write new comments in a language different from the existing comment language of any existing file
8. AI must not overwrite files without reading them first
9. **Modification of this `/AGENTS.md` file is absolutely forbidden**

## License & Legal Requirements

All contributions must comply with licensing requirements. All code must be compatible with the AGPL-3.0-or-later license and the project's additional exemption clause (located at lines 237-245 at the end of the LICENSE file).

## Signed-off-by & DCO

AI agents are **strictly forbidden** from adding Signed-off-by tags.

Only humans can legally certify the DCO.

Human committers are responsible for:

- Reviewing all AI-generated code
- Ensuring compliance with licensing requirements
- Adding their own Signed-off-by tag to certify the DCO
- Taking responsibility for contributions

AI assistants are responsible for:

- Understanding the runtime environment, such as the operating system or specific distribution
- Following the rules outlined in this document
- Proactively reminding developers using AI tools

This document references <a href="https://docs.kernel.org/process/coding-assistants.html" target="_blank" rel="noopener noreferrer">AI Coding Assistants — The Linux Kernel documentation</a>
