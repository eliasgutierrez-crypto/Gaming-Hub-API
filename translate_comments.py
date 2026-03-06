"""Utility to translate comment lines in project files to Spanish.

Usage:
    python translate_comments.py [path...]

If no paths are provided, it will scan the current directory recursively and
process known file types (.py, .js, .vue, .md, .conf, etc.).

The script uses googletrans to translate individual comment lines, leaving
other text intact. It overwrites files after translation, but creates a
.backup copy for safety.

Note: translate_comments.py requires network access for the Google Translate
API used by googletrans. For large configuration files (e.g. redis redis.conf)
it may be safer to review translations manually.
"""

import sys
import re
from googletrans import Translator
from pathlib import Path

# regex patterns for comment markers
COMMENT_PATTERNS = [
    (re.compile(r"^(\s*)#(.*)$"), "#"),  # Python, shell, conf
    (re.compile(r"^(\s*)(//.*)$"), "//"),  # JS, Vue, config
    (re.compile(r"^(\s*)(/\*.*?\*/)$"), "/* */"),  # inline block, ignored
]

translator = Translator()

def translate_line(line: str) -> str:
    for pattern, marker in COMMENT_PATTERNS:
        m = pattern.match(line)
        if m:
            prefix = m.group(1)
            comment = m.group(2)
            # remove leading comment markers and whitespace
            stripped = comment.lstrip('/#* ')  # rough
            if not stripped.strip():
                return line
            # perform translation
            try:
                result = translator.translate(stripped, dest='es')
                translated = result.text
            except Exception as e:
                print(f"translation failed for: {stripped!r} -> {e}")
                return line
            # reconstruct line with original markers
            if marker == '#':
                return f"{prefix}# {translated}"
            elif marker == '//':
                return f"{prefix}// {translated}"
            else:
                return line
    return line


def process_file(path: Path):
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    new_lines = []
    changed = False
    for line in lines:
        new_line = translate_line(line)
        new_lines.append(new_line)
        if new_line != line:
            changed = True
    if changed:
        backup = path.with_suffix(path.suffix + '.bak')
        path.replace(backup)
        path.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
        print(f"Translated comments in {path}, backup saved to {backup}")


def main():
    paths = sys.argv[1:]
    if not paths:
        paths = [str(p) for p in Path('.').rglob('*') if p.is_file()]
    for p in paths:
        path = Path(p)
        if path.suffix.lower() in ['.py', '.js', '.vue', '.md', '.conf', '.ini', '.txt']:
            process_file(path)

if __name__ == '__main__':
    main()
