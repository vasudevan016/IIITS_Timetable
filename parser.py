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
# PART 2: THE HYBRID TIMETABLE PARSER
# ==========================================
import pdfplumber
import json
import os
import re

# 1. YOUR PERFECT, UNCORRUPTED UG1 BACKUP
perfect_ug1 = {
    "Monday": {
      "08:45 AM - 09:45 AM": [
        { "base": "OCW", "course": "OCW", "section": "Sec4", "room": "G08" },
        { "base": "OCW", "course": "OCW", "section": "Sec1", "room": "LAB 103" }
      ],
      "09:45 AM - 10:45 AM": [
        { "base": "OCW", "course": "OCW", "section": "Sec1", "room": "LAB 103" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec2", "room": "G08" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec3", "room": "G07" }
      ],
      "11:00 AM - 12:00 PM": [
        { "base": "DLD", "course": "DLD", "section": "Sec2", "room": "G08" },
        { "base": "CP", "course": "CP", "section": "Sec3", "room": "Lab 103" },
        { "base": "DLD", "course": "DLD", "section": "Sec1", "room": "G09" }
      ],
      "12:00 PM - 01:00 PM": [
        { "base": "DSMA", "course": "DSMA", "section": "Sec4", "room": "G07" },
        { "base": "CP", "course": "CP", "section": "Sec3", "room": "Lab 103" }
      ],
      "02:15 PM - 03:15 PM": [
        { "base": "OCW", "course": "OCW", "section": "Sec2", "room": "Lab 103" },
        { "base": "OCW", "course": "OCW", "section": "Sec3", "room": "G07" },
        { "base": "CP", "course": "CP", "section": "Sec1", "room": "G08" }
      ],
      "03:15 PM - 04:15 PM": [
        { "base": "OCW", "course": "OCW", "section": "Sec2", "room": "Lab 103" },
        { "base": "CP", "course": "CP", "section": "Sec3", "room": "G08" }
      ],
      "04:30 PM - 05:30 PM": [
        { "base": "DSMA", "course": "DSMA", "section": "Sec5", "room": "G04" }
      ]
    },
    "Tuesday": {
      "08:45 AM - 09:45 AM": [
        { "base": "CP", "course": "CP", "section": "Sec4", "room": "Lab 103" },
        { "base": "DLD", "course": "DLD", "section": "Sec1", "room": "Lab 114/102" }
      ],
      "09:45 AM - 10:45 AM": [
        { "base": "CP", "course": "CP", "section": "Sec4", "room": "Lab 103" },
        { "base": "DLD", "course": "DLD", "section": "Sec1", "room": "Lab 114/102" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec3", "room": "G08" },
        { "base": "OCW", "course": "OCW", "section": "Sec2", "room": "G09" }
      ],
      "11:00 AM - 12:00 PM": [
        { "base": "DLD", "course": "DLD", "section": "Sec3", "room": "Lab 114/102" },
        { "base": "DLD", "course": "DLD", "section": "Sec2", "room": "G08" },
        { "base": "DLD", "course": "DLD", "section": "Sec4", "room": "G09" }
      ],
      "12:00 PM - 01:00 PM": [
        { "base": "DLD", "course": "DLD", "section": "Sec3", "room": "Lab 114/102" },
        { "base": "OCW", "course": "OCW", "section": "Sec4", "room": "G08" }
      ],
      "02:15 PM - 03:15 PM": [
        { "base": "OCW", "course": "OCW", "section": "Sec3", "room": "Lab 103" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec2", "room": "G09" },
        { "base": "DLD", "course": "DLD", "section": "Sec1", "room": "B03" }
      ],
      "03:15 PM - 04:15 PM": [
        { "base": "OCW", "course": "OCW", "section": "Sec3", "room": "Lab 103" },
        { "base": "CP", "course": "CP", "section": "Sec2", "room": "G09" },
        { "base": "CP", "course": "CP", "section": "Sec4", "room": "B03" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec1", "room": "G08" }
      ],
      "04:30 PM - 05:30 PM": [
        { "base": "CP", "course": "CP", "section": "Sec1", "room": "G06" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec4", "room": "G09" },
        { "base": "OCW", "course": "OCW", "section": "Sec3", "room": "G07" }
      ]
    },
    "Wednesday": {
      "08:45 AM - 09:45 AM": [
        { "base": "CP", "course": "CP", "section": "Sec1", "room": "Lab 103" },
        { "base": "DLD", "course": "DLD", "section": "Sec4", "room": "LAB 114/102" }
      ],
      "09:45 AM - 10:45 AM": [
        { "base": "CP", "course": "CP", "section": "Sec1", "room": "Lab 103" },
        { "base": "DLD", "course": "DLD", "section": "Sec4", "room": "LAB 114/102" },
        { "base": "DLD", "course": "DLD", "section": "Sec3", "room": "G07" }
      ],
      "11:00 AM - 12:00 PM": [
        { "base": "OCW", "course": "OCW", "section": "Sec1", "room": "G09" },
        { "base": "CP", "course": "CP", "section": "Sec2", "room": "G08" },
        { "base": "DLD", "course": "DLD", "section": "Sec4", "room": "G04" }
      ],
      "12:00 PM - 01:00 PM": [
        { "base": "DSMA", "course": "DSMA", "section": "Sec5", "room": "G09" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec3", "room": "G07" }
      ],
      "02:15 PM - 03:15 PM": [
        { "base": "DLD", "course": "DLD", "section": "Sec4", "room": "G09" }
      ],
      "03:15 PM - 04:15 PM": [
        { "base": "DSMA", "course": "DSMA", "section": "Sec4", "room": "G09" },
        { "base": "DLD", "course": "DLD", "section": "Sec2", "room": "G08" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec1", "room": "G05" }
      ],
      "04:30 PM - 05:30 PM": [
        { "base": "EE", "course": "EE", "section": "Sec2", "room": "G08" }
      ],
      "05:30 PM - 06:30 PM": [
        { "base": "EE", "course": "EE", "section": "Sec2", "room": "G08" }
      ]
    },
    "Thursday": {
      "08:45 AM - 09:45 AM": [
        { "base": "OCW", "course": "OCW", "section": "Sec4", "room": "Lab 103" },
        { "base": "OCW", "course": "OCW", "section": "Sec1", "room": "G08" }
      ],
      "09:45 AM - 10:45 AM": [
        { "base": "OCW", "course": "OCW", "section": "Sec4", "room": "Lab 103" },
        { "base": "CP", "course": "CP", "section": "Sec1", "room": "G09" },
        { "base": "CP", "course": "CP", "section": "Sec3", "room": "G07" }
      ],
      "11:00 AM - 12:00 PM": [
        { "base": "DLD", "course": "DLD", "section": "Sec1", "room": "G09" },
        { "base": "CP", "course": "CP", "section": "Sec2", "room": "lab 103" },
        { "base": "DLD", "course": "DLD", "section": "Sec3", "room": "G07" }
      ],
      "12:00 PM - 01:00 PM": [
        { "base": "CP", "course": "CP", "section": "Sec2", "room": "lab 103" },
        { "base": "OCW", "course": "OCW", "section": "Sec4", "room": "G08" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec1", "room": "G09" }
      ],
      "02:15 PM - 03:15 PM": [
        { "base": "OCW", "course": "OCW", "section": "Sec2", "room": "B05" },
        { "base": "CP", "course": "CP", "section": "Sec4", "room": "G08" }
      ],
      "03:15 PM - 04:15 PM": [
        { "base": "DSMA", "course": "DSMA", "section": "Sec5", "room": "G09" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec2", "room": "G07" }
      ],
      "04:30 PM - 05:30 PM": [
        { "base": "EDL", "course": "EDL", "section": "Sec1", "room": "G08" }
      ],
      "05:30 PM - 06:30 PM": [
        { "base": "EDL", "course": "EDL", "section": "Sec1", "room": "G08" }
      ]
    },
    "Friday": {
      "08:45 AM - 09:45 AM": [
        { "base": "OCW", "course": "OCW", "section": "Sec1", "room": "G09" }
      ],
      "09:45 AM - 10:45 AM": [
        { "base": "DSMA", "course": "DSMA", "section": "Sec4", "room": "G09" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec5", "room": "G08" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec2", "room": "G07" }
      ],
      "11:00 AM - 12:00 PM": [
        { "base": "DLD", "course": "DLD", "section": "Sec3", "room": "G08" },
        { "base": "OCW", "course": "OCW", "section": "Sec2", "room": "G09" }
      ],
      "12:00 PM - 01:00 PM": [
        { "base": "CP", "course": "CP", "section": "Sec3", "room": "G06" },
        { "base": "CP", "course": "CP", "section": "Sec2", "room": "G09" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec1", "room": "G07" }
      ],
      "02:15 PM - 03:15 PM": [
        { "base": "CP", "course": "CP", "section": "Sec4", "room": "G09" },
        { "base": "DSMA", "course": "DSMA", "section": "Sec3", "room": "G08" },
        { "base": "DLD", "course": "DLD", "section": "Sec2", "room": "Lab 114/102" }
      ],
      "03:15 PM - 04:15 PM": [
        { "base": "DLD", "course": "DLD", "section": "Sec2", "room": "Lab 114/102" },
        { "base": "OCW", "course": "OCW", "section": "Sec3", "room": "G07" }
      ],
      "04:30 PM - 05:30 PM": [
        { "base": "EE", "course": "EE", "section": "Sec1", "room": "G06" }
      ],
      "05:30 PM - 06:30 PM": [
        { "base": "EE", "course": "EE", "section": "Sec1", "room": "G06" }
      ]
    },
    "Saturday": {
      "08:45 AM - 09:45 AM": [
        { "base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD" }
      ],
      "09:45 AM - 10:45 AM": [
        { "base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD" }
      ],
      "11:00 AM - 12:00 PM": [
        { "base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD" }
      ],
      "12:00 PM - 01:00 PM": [
        { "base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD" }
      ],
      "02:15 PM - 03:15 PM": [
        { "base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD" }
      ],
      "03:15 PM - 04:15 PM": [
        { "base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD" }
      ],
      "04:30 PM - 05:30 PM": [
        { "base": "EDL", "course": "EDL", "section": "Sec2", "room": "G04" }
      ],
      "05:30 PM - 06:30 PM": [
        { "base": "EDL", "course": "EDL", "section": "Sec2", "room": "G04" }
      ]
    }
}

timetable_db = {"UG1": perfect_ug1, "UG2": {}, "UG3": {}, "UG4": {}}
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# 2. HELPER FUNCTION: Maps sloppy PDF times to your perfect keys
def normalize_time(raw_time):
    raw = raw_time.upper().replace(" ", "").replace("\n", "")
    if "8:45" in raw or "08:45" in raw: return "08:45 AM - 09:45 AM"
    if "9:45" in raw or "09:45" in raw: return "09:45 AM - 10:45 AM"
    if "11:00" in raw: return "11:00 AM - 12:00 PM"
    if "12:00" in raw: return "12:00 PM - 01:00 PM"
    if "1:00" in raw and "2:00" in raw: return "01:00 PM - 02:00 PM"
    if "2:15" in raw or "02:15" in raw: return "02:15 PM - 03:15 PM"
    if "3:15" in raw or "03:15" in raw: return "03:15 PM - 04:15 PM"
    if "4:30" in raw or "04:30" in raw: return "04:30 PM - 05:30 PM"
    if "5:30" in raw or "05:30" in raw: return "05:30 PM - 06:30 PM"
    return raw_time.strip()

timetable_filepath = os.path.join("data", "Time table M2026.pdf")
print("Extracting senior batch room data for Vacant Room Finder...")

if os.path.exists(timetable_filepath):
    try:
        with pdfplumber.open(timetable_filepath) as pdf:
            # SKIP PAGE 0 (UG1). Only scrape UG2, UG3, UG4.
            for page_num in range(1, min(4, len(pdf.pages))):
                page = pdf.pages[page_num]
                batch = f"UG{page_num + 1}"
                
                prev_row_classes = {day: [] for day in days}
                tables = page.extract_tables()
                
                for table in tables:
                    if not table: continue
                    for row in table[1:]:
                        if len(row) < 7: continue 
                        
                        time_slot = row[0] 
                        if not time_slot or "BREAK" in time_slot.upper() or "LUNCH" in time_slot.upper():
                            continue
                        
                        clean_time = normalize_time(time_slot)
                        
                        for i, day in enumerate(days):
                            if i + 1 < len(row) and row[i+1]:
                                classes_raw = [c.strip() for c in row[i+1].split('\n') if c.strip()]
                            else:
                                classes_raw = []
                            
                            if "05:30" in clean_time and not classes_raw:
                                classes_raw = prev_row_classes[day]
                            prev_row_classes[day] = classes_raw
                            
                            if day not in timetable_db[batch]: timetable_db[batch][day] = {}
                            if clean_time not in timetable_db[batch][day]: timetable_db[batch][day][clean_time] = []
                            
                            for class_str in classes_raw:
                                match = re.match(r'^([A-Za-z\-&]+)(\d*)\s+(.*)$', class_str)
                                if match:
                                    room = match.group(3).strip()
                                    timetable_db[batch][day][clean_time].append({"room": room})
                                else:
                                    parts = class_str.split()
                                    room = " ".join(parts[1:]) if len(parts) > 1 else ""
                                    timetable_db[batch][day][clean_time].append({"room": room})
                                    
        with open('timetable.json', 'w') as f:
            json.dump(timetable_db, f, indent=4)
        print("Success: Hybrid timetable generated!")
        
    except Exception as e:
        print(f"Error extracting tables: {e}")
else:
    print("Timetable PDF not found in data folder.")