# Fetch Rimata Reference Data

Tool to fetch aorist and future verb forms from Rimata.app and add them to your Greek verb TSV data.

## Usage

```bash
# Read TSV from stdin, write TSV to stdout
cat input.tsv | python3 fetch_rimata.py > output.tsv

# Or use input redirection
python3 fetch_rimata.py < input.tsv > output.tsv
```

## Input Format

The script expects a TSV file with a verb column. It will automatically detect the verb column if it's named:
- `Ενεστώτας` (Modern Greek - default)
- `Verb` (English)
- `Present` (English)

Required columns: At minimum, one verb column. Other columns are preserved.

Example input:

```tsv
Ενεστώτας	Μετάφραση	Αόριστος	Μέλλοντας
σχολάω	skip school	σχόλασα	θα σχολάσω
γελάω	laugh	γέλασα	θα γελάσω
αγαπάω	love	αγάπησα	θα αγαπήσω
```

## Output Format

The script adds three new columns to the output TSV:

- **`Rimata_Αόριστος`** — Aorist form(s) from Rimata.app
- **`Rimata_Μέλλοντας`** — Future form(s) from Rimata.app
- **`Rimata_Note`** — Error notes (HTTP errors, etc.)

Example output:

```tsv
Ενεστώτας	Μετάφραση	Αόριστος	Μέλλοντας	Rimata_Αόριστος	Rimata_Μέλλοντας	Rimata_Note
σχολάω	skip school	σχόλασα	θα σχολάσω	σχόλασα	θα σχολάσω
γελάω	laugh	γέλασα	θα γελάσω	γέλασα	θα γελάσω
αγαπάω	love	αγάπησα	θα αγαπήσω	αγάπησα	θα αγαπήσω
```

## Output Streams

- **stdout** — TSV data (ready for piping to other tools or redirecting to files)
- **stderr** — Progress log showing:
  - `[N/Total] ✓ verb` — Successfully fetched
  - `[N/Total] ✗ verb` — Failed to fetch (HTTP error or verb not found)
  - `[N/Total] SKIP (empty)` — Skipped empty rows

Example progress:

```
[1/87] ✓ αργώ
[2/87] ✓ έρχομαι
[3/87] ✓ έχω
...
[85/87] ✗ φώναζω HTTP 404
[86/87] ✓ χαιρετάω
[87/87] ✓ χαλάω
```

## Examples

### Fetch Rimata data for all verbs in a file

```bash
cat verbs.tsv | python3 fetch_rimata.py > verbs_with_rimata.tsv 2>fetch.log
```

### View progress while fetching

```bash
cat verbs.tsv | python3 fetch_rimata.py > verbs_with_rimata.tsv
```

Progress is shown in stderr automatically.

### Process file and redirect errors

```bash
python3 fetch_rimata.py < verbs.tsv > verbs_with_rimata.tsv 2>&1 | grep "✗"
```

Shows only failed verbs.

### Chain with other tools

```bash
# Fetch Rimata data and open in LibreOffice Calc
cat verbs.tsv | python3 fetch_rimata.py > /tmp/result.tsv && libreoffice /tmp/result.tsv
```

## Technical Details

### HTTP Requests

- One HTTP GET request per verb to `https://rimata.app/verb/{encoded_verb}`
- Extracts data from HTML using regex patterns
- 0.5 second delay between requests (polite server behavior)

### Verb Normalization

- Handles verb alternatives: `πάω/πηγαίνω` → uses `πάω`
- Strips whitespace from verb names
- Case-sensitive matching

### Error Handling

- HTTP 404 errors logged in `Rimata_Note` column
- Network errors caught and logged
- Invalid/missing verb columns detected with clear error message
- Interrupts gracefully on Ctrl+C (exit code 130)

### Column Detection

The script automatically detects the verb column from these candidates:
1. `Ενεστώτας` (Modern Greek)
2. `Verb`
3. `Present`

If none are found, the script exits with error code 1.

## Performance

- ~87 verbs per ~50 seconds (with 0.5s politeness delay)
- Network bound (limited by Rimata.app response time)
- Minimal memory usage (streaming CSV processing)

## Rimata.app Coverage

- **83/88** verbs in the standard test set available on Rimata
- **4 verbs not found** (HTTP 404):
  - άργω (ancient form?)
  - κατεβαινω (typo variant?)
  - πηυαίνω (malformed?)
  - φώναζω (possibly typo for φωνάζω?)

Note: Rimata returns multiple forms separated by commas when variants exist (e.g., "ήρθα, ήλθα")

## Integration with Test Suite

Use this tool to regenerate reference data:

```bash
# Regenerate Rimata reference columns
cd /home/sadov/work/greek/git/github/modern-greek-inflexion-eee
cat test/data/Ρήματα_Input_for_rimata.tsv | python3 fetch_rimata.py > test/data/Ρήματα_Combined.tsv 2>test/data/fetch_rimata.log

# Verify output
head test/data/Ρήματα_Combined.tsv
```

## Requirements

- Python 3.7+
- pandas library
- Network connection to https://rimata.app/

## License

Tool for testing the modern-greek-inflexion library against Rimata.app reference data.
