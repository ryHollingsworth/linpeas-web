# LinPEAS Web Report Generator

This script parses the output of a `linpeas.sh` scan and generates a categorized, interactive HTML report for easy analysis and review.

## Features

- Parses `linpeas.txt` output and categorizes findings.
- Outputs a responsive HTML report using Bootstrap 5.
- Interactive features: filter/search, print-friendly, dark mode toggle, collapsible sections.
- Automatically serves the HTML report using a local HTTP server.

## Prerequisites

- Python 3.x
- LinPEAS scan result saved as a text file (e.g., `linpeas.txt`)

## Usage

### 1. Run LinPEAS on the target system:

```bash
./linpeas.sh > linpeas.txt
```

Transfer the `linpeas.txt` file to your analysis system if needed.

### 2. Run the Script

```bash
python3 linpeas-web.py linpeas.txt
```

This will:

- Parse and categorize `linpeas.txt`
- Create an output directory `linepeas-web/`
- Generate a file `index.html` inside it
- Start a local web server at [http://localhost:8080](http://localhost:8080)

### 3. View the Report

Open your browser and go to:

```
http://localhost:8080
```

You can use this to navigate and search through LinPEAS findings easily.

## Alternate Manual HTTP Server Start

If you'd like to start the HTTP server manually later:

- **Python 2:**
  ```bash
  cd linepeas-web
  python2 -m SimpleHTTPServer 80
  ```

- **Python 3:**
  ```bash
  cd linepeas-web
  python3 -m http.server 80
  ```

## File Structure

```
├── linpeas.txt              # Input: LinPEAS scan output
├── linpeas-web.py           # This script
└── linepeas-web/
    └── index.html           # Output: Interactive HTML report
```

## License

This tool is open for personal and educational use. Modify as needed for your internal pentesting or CTF workflows.

