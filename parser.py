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
# PART 2: TIMETABLE GRID PARSER
# ==========================================
import pdfplumber

timetable_filepath = os.path.join("data", "Time table M2026.pdf")
timetable_db = {"UG1": {}, "UG2": {}, "UG3": {}, "UG4": {}}
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

print("Scanning for Timetable PDF...")
if os.path.exists(timetable_filepath):
    try:
        with pdfplumber.open(timetable_filepath) as pdf:
            # The schedule spans multiple pages, so we iterate through them
            for page in pdf.pages:
                tables = page.extract_tables()
                
                for table in tables:
                    if not table: continue
                    
                    # Assuming table[0] contains the Days header
                    # table[1:] contains Time in column 0, and Classes in columns 1-6
                    for row in table[1:]:
                        time_slot = row[0] 
                        if not time_slot or "BREAK" in time_slot.upper():
                            continue
                        
                        clean_time = time_slot.replace('\n', '').strip()
                        
                        for i, day in enumerate(days):
                            # Col 0 is time, Col 1 is Monday, Col 2 is Tuesday, etc.
                            if i + 1 < len(row) and row[i+1]:
                                classes_raw = row[i+1].replace('\n', ' ').strip()
                                
                                if day not in timetable_db["UG1"]: 
                                    timetable_db["UG1"][day] = {}
                                if clean_time not in timetable_db["UG1"][day]: 
                                    timetable_db["UG1"][day][clean_time] = []
                                    
                                # You can add custom regex here later to split "OCW4 G08" 
                                # into separate "course", "section", and "room" variables.
                                timetable_db["UG1"][day][clean_time].append({
                                    "raw_text": classes_raw,
                                    "branch": "ALL" # Placeholder until regex is added
                                })
                                
        # Export the compiled timetable database
        with open('timetable.json', 'w') as f:
            json.dump(timetable_db, f, indent=4)
        print("Successfully generated timetable.json!")
        
    except Exception as e:
        print(f"Error extracting tables: {e}")
else:
    print("Timetable PDF not found in data folder.")