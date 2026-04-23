# DF-Description-Generator

A Python + Flask project for generating descriptions of images based on the Fortress Symbol creation tool in Dwarf Fortress. It uses weighted random selection and logical constraints.

---

## Architecture Overview

This project is organized into clearly separated components:
<pre>
sentence_generator/
│
├── core/                          # Sentence generation logic pipeline
│   ├── generator.py               # Orchestrates sentence generation
│   ├── logic.py                   # Determines subject/description counts and constraints for subject-description pairing
│   ├── selector.py                # Selects descriptions and subjects to be used
│   └── grammar.py                 # Formats final sentence text
│
├── data/
│   ├── loader.py                  # Loads all data into a global runtime state
│   └── filters.py                 # Tag and category-based filtering utilities
│
├── cli/                           # Command-line interface logic
│   └── (CLI-related files live here)
│
├── gui/                           # GUI / Flask layer (early stage)
│   └── (routes, templates, or frontend logic will go here)
│
├── resources/                     # Static JSON data files (subjects, descriptions, weights)
│
├── main.py                        # Entry point for running the application
├── __init__.py                    # Package initializer
</pre>
All runtime data is stored in a singleton `GlobalState` object for efficient access across modules.

---

## Features

-  Weighted random selections
-  Tag-based filtering of subjects and descriptions
-  X and XY description structure (1-subject vs 2-subject actions)
-  Sentence formatting with pluralization and article logic

---

## Sample Output

"The image is of multiple Giant elephants. The Giant elephants are suffering"
