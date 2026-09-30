import os
import json
import re
import pdfplumber

pdf_path = os.path.join("data", "Time table M2026.pdf")
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

standard_slots = [
    "08:45 AM - 09:45 AM",
    "09:45 AM - 10:45 AM",
    "11:00 AM - 12:00 PM",
    "12:00 PM - 01:00 PM",
    "02:15 PM - 03:15 PM",
    "03:15 PM - 04:15 PM",
    "04:30 PM - 05:30 PM",
    "05:30 PM - 06:30 PM"
]

def normalize_time(raw):
    if not raw: return ""
    cleaned = re.sub(r'\s+', ' ', raw.replace('\n', ' ')).strip().upper()
    for slot in standard_slots:
        s_start = slot.split(" - ")[0].replace(" ", "")
        if s_start in cleaned.replace(" ", ""):
            return slot
    return cleaned

def parse_cell(cell_text):
    if not cell_text: return []
    entries = []
    lines = [line.strip() for line in cell_text.split('\n') if line.strip()]
    
    for line in lines:
        if any(skip in line.upper() for skip in ["BREAK", "LUNCH", "TIME TABLE", "UG 1", "UG 2", "UG 3", "UG 4"]):
            continue
            
        m = re.match(r'^([A-Za-z]+)(\d*)\s+(.*)$', line)
        if m:
            base = m.group(1).upper()
            sec_num = m.group(2)
            room = m.group(3).strip()
            
            section = f"Sec{sec_num}" if sec_num else ""
            
            # Universal batches
            if base in ["FHVE", "EE", "EDL", "PGP", "QRA", "SEED", "ES"]:
                branch = "ALL"
            else:
                branch = "ALL"

            entries.append({
                "course": f"{base}{sec_num}" if sec_num else base,
                "base": base,
                "section": section,
                "room": room,
                "branch": branch
            })
        else:
            parts = line.split()
            if not parts: continue
            entries.append({
                "course": parts[0],
                "base": parts[0].upper(),
                "section": "",
                "room": " ".join(parts[1:]) if len(parts) > 1 else "",
                "branch": "ALL"
            })
    return entries

timetable_db = {"UG1": {}, "UG2": {}, "UG3": {}, "UG4": {}}
batch_counter = 1

print("Parsing multi-batch PDF...")
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        # Extract ALL tables on the page separately
        tables = page.extract_tables()
        
        for table in tables:
            if not table or len(table) < 3: 
                continue
            
            # Verify this specific table is a schedule by checking for weekdays
            table_text = str(table).upper()
            if "MONDAY" not in table_text or "TUESDAY" not in table_text:
                continue
            
            if batch_counter > 4:
                break
                
            batch = f"UG{batch_counter}"
            timetable_db[batch] = {d: {} for d in days}
            
            for row in table:
                time_raw = row[0]
                if not time_raw: continue
                
                slot_name = normalize_time(time_raw)
                if not any(slot in slot_name for slot in ["AM", "PM"]):
                    continue

                for day_idx, day in enumerate(days):
                    col_idx = day_idx + 1
                    if col_idx < len(row):
                        parsed_entries = parse_cell(row[col_idx])
                        if parsed_entries:
                            timetable_db[batch][day][slot_name] = parsed_entries
                            
            print(f"Successfully mapped {batch}")
            batch_counter += 1

with open("timetable.json", "w") as f:
    json.dump(timetable_db, f, indent=4)

print("Finished! Check timetable.json to verify.")