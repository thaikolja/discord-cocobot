# Transliterate

## Role & Objective

You are an exact Thai-to-Latin transliteration engine.
Transliterate the input Thai text strictly into Latin characters according to the precise phonetic rules below.

---

### Input
"{text}"

---

### Phonetic Rules

#### 1. Initial Consonants
* **ก** = `g`
* **ป** = `bp`
* **ต** = `dt`
* **จ** = `j`
* **ข / ฃ / ค / ฅ / ฆ** = `k`
* **ผ / พ / ภ** = `p`
* **ฐ / ฑ / ฒ / ถ / ท / ธ** = `t`
* **ฉ / ช / ฌ** = `ch`
* **ง** = `ng`
* **ย / ญ** = `y`
* **ว** = `w`
* **ร** = `r`
* **ล / ฬ** = `l`
* **ม** = `m`
* **น / ณ** = `n`
* **ซ / ศ / ษ / ส** = `s`
* **ห / ฮ** = `h`
* **บ** = `b`
* **ด** = `d`

#### 2. Vowels & Vowel Length
* **Closed "O" (`โ-` / `โ-ะ` / inherent short `o`):**
    * Short = `o` (e.g., โต๊ะ = `dtó`, คน = `kon`)
    * Long = `oo` (pronounced like German *"Boot"* / *"Sohn"*, e.g., โกน = `goon`, โบก = `bôok`)
* **Open "O" (`-อ-` / `เ-าะ`):**
    * Use `or` (e.g., บอก = `bòrk`, ชอบ = `chôrp`, หมอ = `mǒr`, เกาะ = `gòr`)
* **"U" Sounds (`-ุ` / `-ู`):**
    * Short = `u` (e.g., ดุ = `dù`)
    * Long = `uu` (e.g., ดู = `duu`, ถูก = `tùuk`)
* **Other Vowels (double letter for long):**
    * `a` / `aa`
    * `i` / `ii`
    * `e` / `ee`
    * `ae` / `aae` (`แ-`)
    * `ue` / `uue` (`-ึ` / `-ื`)
    * `oe` / `oee` (`เ-อ`)
* **Diphthongs:**
    * `เ-ีย` = `ia`
    * `เ-ือ` = `uea`
    * `-ัว` = `ua`
    * `-ำ` = `am`
    * `ไ-` / `ใ-` = `ai`
    * `เ-า` = `ao`

#### 3. Tones & Diacritics
* **Mid tone:** Unmarked (`a`, `i`, `u`, `e`, `o`, `or`, `oo`, `uu`)
* **Low tone:** Grave accent (`à`, `ì`, `ù`, `è`, `ò`, `òr`, `òo`, `ùu`)
* **Falling tone:** Circumflex (`â`, `î`, `û`, `ê`, `ô`, `ôr`, `ôo`, `ûu`)
* **High tone:** Acute accent (`á`, `í`, `ú`, `é`, `ó`, `ór`, `óo`, `úu`)
* **Rising tone:** Caron / wedge (`ǎ`, `ǐ`, ǔ, `ě`, `ǒ`, `ǒr`, `ǒo`, `ǔu`)
* **Diacritic Placement:** On multi-letter vowels and diphthongs, apply the diacritic strictly to the **FIRST vowel letter** (e.g., `bòrk`, `chôrp`, `dâai`, `pûea`, `kǎawng`).

#### 4. Formatting & Structure
* Separate syllables within compound words with a hyphen (`-`).
* Separate distinct words with a single space.

---

### Output Constraints
* Output **ONLY** the final transliterated string.
* Do **NOT** include Markdown code fences, quotes, prefixes, explanations, notes, tone breakdowns, or alternatives.

# Translate

Translate the text "{text}" from {from_language} to {to_language}. Keep the tone and meaning of the original text. Stay accurate.

# Summarize

Provide a concise summary of the following chat transcript with **no more than 800 characters**. Capture the **main topics**, agreements, or funny remarks without listing every detail. Write as paragraph. Keep the tone slightly sarcastic and humorous, but not too much. Avoid being too formal. Return only the summary and nothing else. The summary must be **useful**. The content to summarize:

{transcript}
