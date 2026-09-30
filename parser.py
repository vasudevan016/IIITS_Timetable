import os
import re
import json
import fitz  # PyMuPDF

pdf_files = {
    "CP_DLD_OCW": ["cp_sec1.pdf", "cp_sec2.pdf", "cp_sec3.pdf", "cp_sec4.pdf"],
    "DSMA": ["dsma_sec1.pdf", "dsma_sec2.pdf", "dsma_sec3.pdf", "dsma_sec4.pdf", "dsma_sec5.pdf"],
    "EE": ["ee_sec1.pdf", "ee_sec2.pdf"],
    "EDL": ["edl_sec1.pdf", "edl_sec2.pdf"]
}

student_db = {}

for course, files in pdf_files.items():
    for filename in files:
        filepath = os.path.join("data", filename)
        
        if not os.path.exists(filepath):
            continue
            
        section_match = re.search(r'sec(\d)', filename.lower())
        section = f"Sec{section_match.group(1)}" if section_match else "Unknown"

        try:
            doc = fitz.open(filepath)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            words = text.split()
            
            for i, word in enumerate(words):
                if "@iiits.in" in word.lower():
                    email = word.lower().strip()
                    
                    if email not in student_db:
                        student_db[email] = {
                            "Name": None,
                            "Roll": None,
                            "Branch": None,
                            "Sections": {}
                        }
                    
                    # Scan ahead up to 25 words to find the Roll Number
                    for j in range(1, 25):
                        if i + j < len(words):
                            check_word = words[i+j].upper()
                            
                            # Lock onto the Roll Number
                            if re.match(r'^S202\d+', check_word):
                                if not student_db[email]["Roll"]:
                                    student_db[email]["Roll"] = check_word
                                
                                # Extract Name ONLY if we haven't grabbed it successfully yet
                                if not student_db[email]["Name"]:
                                    raw_name_words = words[i+1 : i+j]
                                    
                                    # Clean out the garbage (digits, '|', etc.)
                                    clean_name = [w for w in raw_name_words if not re.match(r'^[\d\|]+$', w) and w != '|']
                                    
                                    if clean_name:
                                        student_db[email]["Name"] = " ".join(clean_name).title()
                            
                            # Lock onto the Branch
                            if check_word in ["ECE", "CSE", "AI&DS", "AIDS"] and not student_db[email]["Branch"]:
                                student_db[email]["Branch"] = check_word
                    
                    student_db[email]["Sections"][course] = section
                    
        except Exception as e:
            pass

# Export the compiled database
with open('students.json', 'w') as f:
    json.dump(student_db, f, indent=4)
# ==========================================
# PART 2: TIMETABLE GRID PARSER (PERFECTED)
# ==========================================
import pdfplumber
import json
import os
import re

timetable_filepath = os.path.join("data", "Time table M2026.pdf")
timetable_db = {"UG1": {}, "UG2": {}, "UG3": {}, "UG4": {}}
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

print("Scanning for Timetable PDF...")
if os.path.exists(timetable_filepath):
    try:
        with pdfplumber.open(timetable_filepath) as pdf:
            for page_num, page in enumerate(pdf.pages):
                batch = f"UG{page_num + 1}"
                if batch not in timetable_db: break 
                
                # Memory cache to fix the PDF's missing lines for 2-hour afternoon classes
                prev_row_classes = {day: [] for day in days}
                
                tables = page.extract_tables()
                for table in tables:
                    if not table: continue
                    
                    for row in table[1:]:
                        if len(row) < 7: continue 
                        
                        time_slot = row[0] 
                        if not time_slot or "BREAK" in time_slot.upper() or "LUNCH" in time_slot.upper():
                            continue
                        
                        # Clean dirty PDF time formatting (e.g., fixing "05:\n30 PM")
                        clean_time = re.sub(r'\s+', ' ', time_slot.replace('\n', ' ')).strip()
                        clean_time = clean_time.replace(': ', ':')
                        if '-' in clean_time and ' - ' not in clean_time:
                            clean_time = clean_time.replace('-', ' - ')
                        
                        for i, day in enumerate(days):
                            if i + 1 < len(row) and row[i+1]:
                                classes_raw = [c.strip() for c in row[i+1].split('\n') if c.strip()]
                            else:
                                classes_raw = []
                                
                            # FIX: If the 5:30 slot is empty, pull down the 2-hour class from 4:30
                            if "05:30" in clean_time and not classes_raw:
                                classes_raw = prev_row_classes[day]
                                
                            prev_row_classes[day] = classes_raw
                            
                            if day not in timetable_db[batch]: 
                                timetable_db[batch][day] = {}
                            if clean_time not in timetable_db[batch][day]: 
                                timetable_db[batch][day][clean_time] = []
                                
                            for class_str in classes_raw:
                                match = re.match(r'^([A-Za-z\-&]+)(\d*)\s+(.*)$', class_str)
                                if match:
                                    base = match.group(1).upper()
                                    sec_num = match.group(2)
                                    room = match.group(3).strip()
                                    
                                    # Strict section locking
                                    branch = "" if sec_num else "ALL"
                                    section = f"Sec{sec_num}" if sec_num else ""
                                        
                                    timetable_db[batch][day][clean_time].append({
                                        "course": f"{base}{sec_num}" if sec_num else base,
                                        "base": base,
                                        "section": section,
                                        "room": room,
                                        "branch": branch
                                    })
                                else:
                                    parts = class_str.split()
                                    timetable_db[batch][day][clean_time].append({
                                        "course": parts[0] if parts else class_str,
                                        "base": parts[0].upper() if parts else class_str,
                                        "section": "",
                                        "room": " ".join(parts[1:]) if len(parts) > 1 else "",
                                        "branch": "ALL" 
                                    })
                                    
        with open('timetable.json', 'w') as f:
            json.dump(timetable_db, f, indent=4)
        print("Successfully repaired and generated timetable.json!")
        
    except Exception as e:
        print(f"Error extracting tables: {e}")
else:
    print("Timetable PDF not found in data folder.")