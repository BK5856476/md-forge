# MDForge (AI Skills Repository)

A collection of AI-ready tools (Skills) designed to automate Markdown workflows, content management, and assets organization.

---

## 🏛️ Architecture Overview

MDForge follows a **"Global Workspace, Modular Skills"** architecture. This design ensures that all automation tools share a common data area while maintaining independent logic and instructions.

### 📁 Structure Tree
```text
md-forge/
├── README.md               # [English] Project Overview & Navigation
├── run_all_skills.bat       # [Master Runner] Executes all skills sequentially
├── .gitignore              # Global git ignore rules
├── LICENSE                 # MIT License
├── Clippings/              # [Global Shared Area] Input/Output Workspace
│   └── assets/             # Managed Assets produced by skills
└── skills/                 # Skills container (Infinite extensibility)
    ├── md-image-forge/      # [Skill] Markdown Image Organization
    │   ├── SKILL.md        # AI instruction definition (Chinese)
    │   ├── README.md       # Skill documentation (Chinese)
    │   ├── process_images.bat # Manual execution script
    │   └── scripts/        # Internal logic
    └── md-format-standardizer/ # [Skill] Markdown Formatting
        ├── SKILL.md        # AI instruction definition (Chinese)
        ├── README.md       # Skill documentation (Chinese)
        ├── process_format.bat # Manual execution script
        └── scripts/        # Internal logic
```

### 🎯 Key Design Concepts
1.  **Unified Inbox (Clippings/)**: A shared "Inbox/Outbox" for all skills. You drop your Markdown files at the root, and any enabled skill can process them.
2.  **Self-Contained Skills**: Each folder in `skills/` is a standalone "Skill". It contains its own `SKILL.md` (metadata for AI) and `scripts/`.
3.  **Master Scheduling**: The root `run_all_skills.bat` provides a convenient way to sequence multiple skills (e.g., first fetch images, then standardizing formatting).
4.  **AI-Agent Ready**: Built with **SKILL.md** specifications, allowing AI assistants like Antigravity to discover, understand, and execute your tools automatically.

---

## 🚀 How to Run Skills

### Option 1: Sequential Execution (All Skills)
Run the **`run_all_skills.bat`** in the repository root. This script will iterate through the `skills/` directory and execute every available skill in sequence.

### Option 2: Individual Execution
Navigate to the specific skill directory (e.g., `skills/md-format-standardizer/`) and double-click its local `.bat` file (e.g., `process_format.bat`).

---

## 🛠️ Available Skills

### 🖼️ [Markdown Image Forge](skills/md-image-forge/)
**Purpose**: Automatically handles images in Markdown documents by downloading web images and migrating local images to a structured directory.

### ✍️ [Markdown Format Standardizer](skills/md-format-standardizer/)
**Purpose**: Standardizes Markdown text formatting. 
**Features**:
- Removes metadata blocks and separators.
- Extracts author names and cleans footers.
- Localizes formatting: link flattening, code block fix, and emoji removal.
- New: Compact list layout.

---

## 📜 License
This repository and all its skills are licensed under the **MIT License**.
