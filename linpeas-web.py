#!/usr/bin/env python3
import os, re, html, sys, subprocess
from datetime import datetime

INPUT_FILE = 'linpeas.txt'
OUTPUT_DIR = 'linepeas-web'
OUTPUT_HTML = os.path.join(OUTPUT_DIR, 'index.html')

SECTION_HEADER_RE = re.compile(r'╔[═]+╣ (.+)')
ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*m')

def parse_linpeas_sections(file_path):
    if not os.path.exists(file_path):
        return []

    sections = []
    current_title = None
    current_content = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            clean_line = ANSI_ESCAPE_RE.sub('', line.strip())
            match = SECTION_HEADER_RE.match(clean_line)
            if match:
                if current_title and ''.join(current_content).strip():
                    sections.append((current_title, ''.join(current_content)))
                current_title = match.group(1).strip()
                current_content = []
            elif current_title:
                current_content.append(line)

        if current_title and ''.join(current_content).strip():
            sections.append((current_title, ''.join(current_content)))

    return sections

def ansi_to_html(text):
    text = html.escape(text)
    ansi_map = {
        '\x1b[1;31;103m': '<span class="color-red-bg-yellow">',
        '\x1b[1;31m': '<span class="color-red">',
        '\x1b[1;32m': '<span class="color-green">',
        '\x1b[1;34m': '<span class="color-blue">',
        '\x1b[1;96m': '<span class="color-cyan">',
        '\x1b[1;95m': '<span class="color-magenta">',
        '\x1b[0m': '</span>',
        '\x1b[3m': '<span class="italic">',
        '\x1b[1;90m': '<span class="color-gray">',
    }
    for ansi, replacement in ansi_map.items():
        text = text.replace(ansi, replacement)
    return text

def categorize_section(title):
    title_lower = title.lower()
    if 'password' in title_lower or 'hash' in title_lower:
        return 'Authentication'
    elif 'net' in title_lower or 'ip' in title_lower or 'port' in title_lower:
        return 'Networking'
    elif 'perm' in title_lower or 'writable' in title_lower or 'suid' in title_lower:
        return 'Permissions'
    elif 'user' in title_lower or 'group' in title_lower:
        return 'Users & Groups'
    elif 'process' in title_lower or 'service' in title_lower:
        return 'Processes & Services'
    elif 'docker' in title_lower or 'container' in title_lower:
        return 'Containers'
    elif 'file' in title_lower or 'dir' in title_lower:
        return 'Filesystem'
    else:
        return 'Miscellaneous'

def generate_html(sections, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    report_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    categorized = {}
    for title, content in sections:
        cat = categorize_section(title)
        categorized.setdefault(cat, []).append((title, content))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang="en" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <title>LinPEAS Web Report</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 2rem; }
        .accordion-button:not(.collapsed) { background-color: #e9f2ff; }
        pre { white-space: pre-wrap; word-wrap: break-word; background-color: #f8f9fa; padding: 1rem; }
        .color-red { color: #dc3545; font-weight: bold; }
        .color-green { color: #28a745; font-weight: bold; }
        .color-blue { color: #007bff; font-weight: bold; }
        .color-cyan { color: #17a2b8; font-weight: bold; }
        .color-magenta { color: #e83e8c; font-weight: bold; }
        .italic { font-style: italic; }
        .color-gray { color: #6c757d; }
         .color-red-bg-yellow {
           color: #dc3545;
           background-color: #fff3cd;
           font-weight: bold;
           padding: 0 2px;
           border-radius: 3px;
         }        
.category-title { margin-top: 2rem; font-size: 1.5rem; border-bottom: 2px solid #ccc; padding-bottom: .5rem; }
        @media print {
            .no-print { display: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">LinPEAS Report</h1>
        <p class="text-muted">Generated on: """ + report_timestamp + """</p>
        <div class="mb-4 no-print">
            <button class="btn btn-sm btn-dark me-2" onclick="toggleTheme()">Toggle Dark Mode</button>
            <button class="btn btn-sm btn-primary me-2" onclick="expandAll()">Expand All</button>
            <button class="btn btn-sm btn-secondary me-2" onclick="collapseAll()">Collapse All</button>
            <button class="btn btn-sm btn-outline-info" onclick="window.print()">Print/PDF</button>
            <input type="text" class="form-control mt-3" placeholder="Filter sections..." onkeyup="filterSections(this.value)">
        </div>

        <div id="toc" class="mb-4 no-print">
              <div class="d-flex justify-content-between align-items-center">
                <h4 class="mb-0">Table of Contents</h4>
                <button class="btn btn-sm btn-outline-secondary" onclick="toggleTOC()">Hide TOC</button>
              </div>
            <div id="toc-body">
              <ul>
""")
        idx = 0
        for cat, items in categorized.items():
            f.write(f'<li><strong>{cat}</strong><ul>\n')
            for title, content in items:
                f.write(f'<li><a href="#section-{idx}">{title}</a></li>\n')
                idx += 1
            f.write('</ul></li>\n')

        f.write("""</ul></div></div><div class="accordion" id="linpeasAccordion">\n""")

        idx = 0
        for cat, items in categorized.items():
            #f.write(f'<div class="category-title">{cat}</div>\n')
            f.write(f'<div class="category-group" data-category="{cat}">\n')
            f.write(f'<div class="category-title">{cat}</div>\n')
            for title, content in items:
                if not content.strip(): continue
                safe_id = f"section-{idx}"
                header_id = f"heading-{idx}"
                collapse_id = f"collapse-{idx}"
                f.write(f"""
<div class="accordion-item" id="{safe_id}">
    <h2 class="accordion-header" id="{header_id}">
        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#{collapse_id}" aria-expanded="false" aria-controls="{collapse_id}">
            {title}
        </button>
    </h2>
    <div id="{collapse_id}" class="accordion-collapse collapse" aria-labelledby="{header_id}" data-bs-parent="#linpeasAccordion">
        <div class="accordion-body">
            <pre>{ansi_to_html(content)}</pre>
        </div>
    </div>
</div>
""")
                idx += 1
        f.write('</div>\n')
        f.write("""</div></div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
function expandAll() {
    document.querySelectorAll('.accordion-collapse').forEach(c => new bootstrap.Collapse(c, { show: true }));
}
function collapseAll() {
    document.querySelectorAll('.accordion-collapse').forEach(c => new bootstrap.Collapse(c, { toggle: false }));
}
function toggleTheme() {
    const html = document.querySelector('html');
    html.setAttribute('data-bs-theme', html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark');
}

function filterSections(query) {
    const sections = document.querySelectorAll('.accordion-item');
    query = query.toLowerCase();

    sections.forEach(section => {
        const header = section.querySelector('.accordion-button').textContent.toLowerCase();
        section.style.display = header.includes(query) ? '' : 'none';
    });

    document.querySelectorAll('.category-group').forEach(group => {
        const visibleItems = group.querySelectorAll('.accordion-item:not([style*="display: none"])');
        group.style.display = visibleItems.length ? '' : 'none';
    });
}

function toggleTOC() {
    const toc = document.getElementById("toc-body");
    const btn = event.target;
    if (toc.style.display === "none") {
        toc.style.display = "block";
        btn.textContent = "Hide TOC";
    } else {
        toc.style.display = "none";
        btn.textContent = "Show TOC";
    }
}

</script>
</body></html>""")


if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    parsed_sections = parse_linpeas_sections(input_file)
    generate_html(parsed_sections, OUTPUT_HTML)    
    os.chdir(OUTPUT_DIR)
    try:
      print("Serving report at http://localhost:8080 (Ctrl+C to stop)")
      subprocess.run(["python3", "-m", "http.server", "8080"])
    except KeyboardInterrupt:
      print("\nWeb server stopped.")
