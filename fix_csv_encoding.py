import csv
from pathlib import Path
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def convert_csv_to_excel_utf8(file_path: Path):
    if not file_path.exists():
        return
    
    # Read existing content
    raw_bytes = file_path.read_bytes()
    
    # Try decoding
    text = None
    for enc in ["utf-8-sig", "utf-8", "cp1251"]:
        try:
            text = raw_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue
            
    if text is None:
        print(f"Failed to decode {file_path.name}")
        return

    # Detect delimiter
    lines = text.splitlines()
    if not lines:
        return
    
    first_line = lines[0]
    # Check if delimiter is comma or semicolon
    delim = ";" if ";" in first_line else ","
    
    reader = csv.reader(lines, delimiter=delim)
    rows = [row for row in reader if row]
    
    # Write back as utf-8-sig with semicolon delimiter
    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerows(rows)
        
    print(f"Converted {file_path.name}: {len(rows)} rows -> utf-8-sig with ';' delimiter")

def main():
    dirs_to_check = [
        Path("data"),
        Path("f:/Downloads/AI - Agents/Job_Search_Agent/data")
    ]
    for d in dirs_to_check:
        if d.exists():
            for p in d.glob("*.csv"):
                convert_csv_to_excel_utf8(p)

if __name__ == "__main__":
    main()
