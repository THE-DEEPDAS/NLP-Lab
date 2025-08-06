# Noun Morphology Finite State Transducer (FST)

## Overview
This project implements a Finite State Transducer (FST) for analyzing and generating singular and plural forms of English nouns. The FST handles regular pluralization rules, irregular nouns, and validates nouns using a corpus.

## Approach

### 1. **Irregular Nouns Handling**
- A dictionary of common irregular nouns is maintained for both singular-to-plural and plural-to-singular mappings.
- Examples:
  - Singular: `child` -> Plural: `children`
  - Singular: `man` -> Plural: `men`

### 2. **Validation of Nouns**
- A set of valid nouns is loaded from the Brown corpus (`brown_nouns.txt`).
- If the corpus is not available, basic heuristic rules are applied to validate nouns.
  - Example heuristics:
    - Words shorter than 2 characters are invalid.
    - Words ending with `-ing`, `-ed`, or `-ly` are invalid unless they are exceptions (e.g., `ring`, `king`).

### 3. **Pluralization Rules**
The FST applies the following rules to generate plural forms:

#### a. **E-Insertion Rule**
- Adds `-es` after words ending with `-s`, `-z`, `-x`, `-ch`, or `-sh`.
  - Examples:
    - `fox` -> `foxes`
    - `watch` -> `watches`

#### b. **Y-Replacement Rule**
- Replaces `-y` with `-ies` if the word ends with `-y` and the preceding character is not a vowel.
  - Examples:
    - `baby` -> `babies`
    - `city` -> `cities`

#### c. **S-Addition Rule**
- Adds `-s` to the end of the word for all other cases.
  - Examples:
    - `bag` -> `bags`
    - `cat` -> `cats`

### 4. **Singularization Rules**
The FST applies the following rules to derive singular forms from plurals:

#### a. **Irregular Plurals**
- Uses the reverse mapping of irregular plurals to derive singular forms.
  - Examples:
    - `children` -> `child`
    - `men` -> `man`

#### b. **IES to Y Rule**
- Replaces `-ies` with `-y` for words ending with `-ies`.
  - Examples:
    - `babies` -> `baby`
    - `cities` -> `city`

#### c. **ES Removal Rule**
- Removes `-es` for words ending with `-es` if the singular form ends with `-s`, `-z`, `-x`, `-ch`, or `-sh`.
  - Examples:
    - `foxes` -> `fox`
    - `watches` -> `watch`

#### d. **S Removal Rule**
- Removes the final `-s` for all other cases.
  - Examples:
    - `bags` -> `bag`
    - `cats` -> `cat`

### 5. **Interactive Analysis**
- The program allows users to input words interactively to analyze their singular/plural forms.
- Example:
  ```
  Enter a word to analyze: fox
  Analysis: fox = fox+N+SG

  Enter a word to analyze: foxes
  Analysis: foxes = fox+N+PL
  ```

### 6. **Demonstration of Rules**
- The `demonstrate_rules` method showcases the application of pluralization and singularization rules on a predefined set of examples.

## File Structure
- `q2.py`: Main script containing the FST implementation.
- `brown_nouns.txt`: Corpus of valid nouns used for validation.

## How to Run
1. Ensure `brown_nouns.txt` is in the same directory as `q2.py`.
2. Run the script:
   ```
   python q2.py
   ```
3. Follow the interactive prompts to analyze words.

