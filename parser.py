import os
import re
import json
import fitz  # PyMuPDF

# ==========================================
# PART 1: STUDENT DATABASE PARSER
# ==========================================
print("⏳ Building Student Database from section PDFs...")
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
        if not os.path.exists(filepath): continue
            
        section_match = re.search(r'sec(\d)', filename.lower())
        section = f"Sec{section_match.group(1)}" if section_match else "Unknown"

        try:
            doc = fitz.open(filepath)
            text = ""
            for page in doc: text += page.get_text()
            doc.close()
            
            words = text.split()
            for i, word in enumerate(words):
                if "@iiits.in" in word.lower():
                    email = word.lower().strip()
                    if email not in student_db:
                        student_db[email] = { "Name": None, "Roll": None, "Branch": None, "Sections": {} }
                    
                    for j in range(1, 25):
                        if i + j < len(words):
                            check_word = words[i+j].upper()
                            if re.match(r'^S202\d+', check_word):
                                if not student_db[email]["Roll"]: student_db[email]["Roll"] = check_word
                                if not student_db[email]["Name"]:
                                    raw_name_words = words[i+1 : i+j]
                                    clean_name = [w for w in raw_name_words if not re.match(r'^[\d\|]+$', w) and w != '|']
                                    if clean_name: student_db[email]["Name"] = " ".join(clean_name).title()
                            
                            if check_word in ["ECE", "CSE", "AI&DS", "AIDS"] and not student_db[email]["Branch"]:
                                student_db[email]["Branch"] = check_word
                    
                    student_db[email]["Sections"][course] = section
        except Exception as e:
            pass

with open('students.json', 'w') as f:
    json.dump(student_db, f, indent=4)
print("✅ Successfully generated students.json")

# ==========================================
# PART 2: FLAWLESS HARDCODED TIMETABLE
# ==========================================
print("⏳ Generating Perfect Timetable.json...")

perfect_ug1 = {
    "Monday": {
      "08:45 AM - 09:45 AM": [{"base": "OCW", "course": "OCW", "section": "Sec4", "room": "G08"}, {"base": "OCW", "course": "OCW", "section": "Sec1", "room": "LAB 103"}],
      "09:45 AM - 10:45 AM": [{"base": "OCW", "course": "OCW", "section": "Sec1", "room": "LAB 103"}, {"base": "DSMA", "course": "DSMA", "section": "Sec2", "room": "G08"}, {"base": "DSMA", "course": "DSMA", "section": "Sec3", "room": "G07"}],
      "11:00 AM - 12:00 PM": [{"base": "DLD", "course": "DLD", "section": "Sec2", "room": "G08"}, {"base": "CP", "course": "CP", "section": "Sec3", "room": "Lab 103"}, {"base": "DLD", "course": "DLD", "section": "Sec1", "room": "G09"}],
      "12:00 PM - 01:00 PM": [{"base": "DSMA", "course": "DSMA", "section": "Sec4", "room": "G07"}, {"base": "CP", "course": "CP", "section": "Sec3", "room": "Lab 103"}],
      "02:15 PM - 03:15 PM": [{"base": "OCW", "course": "OCW", "section": "Sec2", "room": "Lab 103"}, {"base": "OCW", "course": "OCW", "section": "Sec3", "room": "G07"}, {"base": "CP", "course": "CP", "section": "Sec1", "room": "G08"}],
      "03:15 PM - 04:15 PM": [{"base": "OCW", "course": "OCW", "section": "Sec2", "room": "Lab 103"}, {"base": "CP", "course": "CP", "section": "Sec3", "room": "G08"}],
      "04:30 PM - 05:30 PM": [{"base": "DSMA", "course": "DSMA", "section": "Sec5", "room": "G04"}],
      "05:30 PM - 06:30 PM": []
    },
    "Tuesday": {
      "08:45 AM - 09:45 AM": [{"base": "CP", "course": "CP", "section": "Sec4", "room": "Lab 103"}, {"base": "DLD", "course": "DLD", "section": "Sec1", "room": "Lab 114/102"}],
      "09:45 AM - 10:45 AM": [{"base": "CP", "course": "CP", "section": "Sec4", "room": "Lab 103"}, {"base": "DLD", "course": "DLD", "section": "Sec1", "room": "Lab 114/102"}, {"base": "DSMA", "course": "DSMA", "section": "Sec3", "room": "G08"}, {"base": "OCW", "course": "OCW", "section": "Sec2", "room": "G09"}],
      "11:00 AM - 12:00 PM": [{"base": "DLD", "course": "DLD", "section": "Sec3", "room": "Lab 114/102"}, {"base": "DLD", "course": "DLD", "section": "Sec2", "room": "G08"}, {"base": "DLD", "course": "DLD", "section": "Sec4", "room": "G09"}],
      "12:00 PM - 01:00 PM": [{"base": "DLD", "course": "DLD", "section": "Sec3", "room": "Lab 114/102"}, {"base": "OCW", "course": "OCW", "section": "Sec4", "room": "G08"}],
      "02:15 PM - 03:15 PM": [{"base": "OCW", "course": "OCW", "section": "Sec3", "room": "Lab 103"}, {"base": "DSMA", "course": "DSMA", "section": "Sec2", "room": "G09"}, {"base": "DLD", "course": "DLD", "section": "Sec1", "room": "B03"}],
      "03:15 PM - 04:15 PM": [{"base": "OCW", "course": "OCW", "section": "Sec3", "room": "Lab 103"}, {"base": "CP", "course": "CP", "section": "Sec2", "room": "G09"}, {"base": "CP", "course": "CP", "section": "Sec4", "room": "B03"}, {"base": "DSMA", "course": "DSMA", "section": "Sec1", "room": "G08"}],
      "04:30 PM - 05:30 PM": [{"base": "CP", "course": "CP", "section": "Sec1", "room": "G06"}, {"base": "DSMA", "course": "DSMA", "section": "Sec4", "room": "G09"}, {"base": "OCW", "course": "OCW", "section": "Sec3", "room": "G07"}],
      "05:30 PM - 06:30 PM": []
    },
    "Wednesday": {
      "08:45 AM - 09:45 AM": [{"base": "CP", "course": "CP", "section": "Sec1", "room": "Lab 103"}, {"base": "DLD", "course": "DLD", "section": "Sec4", "room": "LAB 114/102"}],
      "09:45 AM - 10:45 AM": [{"base": "CP", "course": "CP", "section": "Sec1", "room": "Lab 103"}, {"base": "DLD", "course": "DLD", "section": "Sec4", "room": "LAB 114/102"}, {"base": "DLD", "course": "DLD", "section": "Sec3", "room": "G07"}],
      "11:00 AM - 12:00 PM": [{"base": "OCW", "course": "OCW", "section": "Sec1", "room": "G09"}, {"base": "CP", "course": "CP", "section": "Sec2", "room": "G08"}, {"base": "DLD", "course": "DLD", "section": "Sec4", "room": "G04"}],
      "12:00 PM - 01:00 PM": [{"base": "DSMA", "course": "DSMA", "section": "Sec5", "room": "G09"}, {"base": "DSMA", "course": "DSMA", "section": "Sec3", "room": "G07"}],
      "02:15 PM - 03:15 PM": [{"base": "DLD", "course": "DLD", "section": "Sec4", "room": "G09"}],
      "03:15 PM - 04:15 PM": [{"base": "DSMA", "course": "DSMA", "section": "Sec4", "room": "G09"}, {"base": "DLD", "course": "DLD", "section": "Sec2", "room": "G08"}, {"base": "DSMA", "course": "DSMA", "section": "Sec1", "room": "G05"}],
      "04:30 PM - 05:30 PM": [{"base": "EE", "course": "EE", "section": "Sec2", "room": "G08"}],
      "05:30 PM - 06:30 PM": [{"base": "EE", "course": "EE", "section": "Sec2", "room": "G08"}]
    },
    "Thursday": {
      "08:45 AM - 09:45 AM": [{"base": "OCW", "course": "OCW", "section": "Sec4", "room": "Lab 103"}, {"base": "OCW", "course": "OCW", "section": "Sec1", "room": "G08"}],
      "09:45 AM - 10:45 AM": [{"base": "OCW", "course": "OCW", "section": "Sec4", "room": "Lab 103"}, {"base": "CP", "course": "CP", "section": "Sec1", "room": "G09"}, {"base": "CP", "course": "CP", "section": "Sec3", "room": "G07"}],
      "11:00 AM - 12:00 PM": [{"base": "DLD", "course": "DLD", "section": "Sec1", "room": "G09"}, {"base": "CP", "course": "CP", "section": "Sec2", "room": "lab 103"}, {"base": "DLD", "course": "DLD", "section": "Sec3", "room": "G07"}],
      "12:00 PM - 01:00 PM": [{"base": "CP", "course": "CP", "section": "Sec2", "room": "lab 103"}, {"base": "OCW", "course": "OCW", "section": "Sec4", "room": "G08"}, {"base": "DSMA", "course": "DSMA", "section": "Sec1", "room": "G09"}],
      "02:15 PM - 03:15 PM": [{"base": "OCW", "course": "OCW", "section": "Sec2", "room": "B05"}, {"base": "CP", "course": "CP", "section": "Sec4", "room": "G08"}],
      "03:15 PM - 04:15 PM": [{"base": "DSMA", "course": "DSMA", "section": "Sec5", "room": "G09"}, {"base": "DSMA", "course": "DSMA", "section": "Sec2", "room": "G07"}],
      "04:30 PM - 05:30 PM": [{"base": "EDL", "course": "EDL", "section": "Sec1", "room": "G08"}],
      "05:30 PM - 06:30 PM": [{"base": "EDL", "course": "EDL", "section": "Sec1", "room": "G08"}]
    },
    "Friday": {
      "08:45 AM - 09:45 AM": [{"base": "OCW", "course": "OCW", "section": "Sec1", "room": "G09"}],
      "09:45 AM - 10:45 AM": [{"base": "DSMA", "course": "DSMA", "section": "Sec4", "room": "G09"}, {"base": "DSMA", "course": "DSMA", "section": "Sec5", "room": "G08"}, {"base": "DSMA", "course": "DSMA", "section": "Sec2", "room": "G07"}],
      "11:00 AM - 12:00 PM": [{"base": "DLD", "course": "DLD", "section": "Sec3", "room": "G08"}, {"base": "OCW", "course": "OCW", "section": "Sec2", "room": "G09"}],
      "12:00 PM - 01:00 PM": [{"base": "CP", "course": "CP", "section": "Sec3", "room": "G06"}, {"base": "CP", "course": "CP", "section": "Sec2", "room": "G09"}, {"base": "DSMA", "course": "DSMA", "section": "Sec1", "room": "G07"}],
      "02:15 PM - 03:15 PM": [{"base": "CP", "course": "CP", "section": "Sec4", "room": "G09"}, {"base": "DSMA", "course": "DSMA", "section": "Sec3", "room": "G08"}, {"base": "DLD", "course": "DLD", "section": "Sec2", "room": "Lab 114/102"}],
      "03:15 PM - 04:15 PM": [{"base": "DLD", "course": "DLD", "section": "Sec2", "room": "Lab 114/102"}, {"base": "OCW", "course": "OCW", "section": "Sec3", "room": "G07"}],
      "04:30 PM - 05:30 PM": [{"base": "EE", "course": "EE", "section": "Sec1", "room": "G06"}],
      "05:30 PM - 06:30 PM": [{"base": "EE", "course": "EE", "section": "Sec1", "room": "G06"}]
    },
    "Saturday": {
      "08:45 AM - 09:45 AM": [{"base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD"}],
      "09:45 AM - 10:45 AM": [{"base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD"}],
      "11:00 AM - 12:00 PM": [{"base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD"}],
      "12:00 PM - 01:00 PM": [{"base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD"}],
      "02:15 PM - 03:15 PM": [{"base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD"}],
      "03:15 PM - 04:15 PM": [{"base": "FHVE", "course": "FHVE", "branch": "ALL", "room": "TBD"}],
      "04:30 PM - 05:30 PM": [{"base": "EDL", "course": "EDL", "section": "Sec2", "room": "G04"}],
      "05:30 PM - 06:30 PM": [{"base": "EDL", "course": "EDL", "section": "Sec2", "room": "G04"}]
    }
}

raw_ug2 = {
    "Monday": {"08:45 AM - 09:45 AM": ["PC2 B05", "OOP4 G05", "RANAC1 G06"], "09:45 AM - 10:45 AM": ["RANAC2 G04", "CS B03", "ADSA1 G06"], "11:00 AM - 12:00 PM": ["OS2 B03", "DBMS1 G05", "CNA G06", "DBMS3 G07"], "12:00 PM - 01:00 PM": ["OS1 G04", "OS3 G06", "ML 109"], "02:15 PM - 03:15 PM": ["DBMS2 G04", "ADSA3 G05", "RANAC4 G09"], "03:15 PM - 04:15 PM": ["RANAC3 G04", "ADSA2 G05", "OOP4 G07"], "04:30 PM - 05:30 PM": ["OOP2 Lab 103", "PC3 Lab B05"], "05:30 PM - 06:30 PM": ["OOP2 Lab 103", "PC3 Lab B05"]},
    "Tuesday": {"08:45 AM - 09:45 AM": ["PC1 B05", "RANAC3 G05", "CNA G06"], "09:45 AM - 10:45 AM": ["OOP1 G04", "CS G05"], "11:00 AM - 12:00 PM": ["OOP3 Lab 103", "DBMS1 G04", "OOP2 G05"], "12:00 PM - 01:00 PM": ["OOP3 Lab 103", "PC4 G04", "RANAC2 G06"], "02:15 PM - 03:15 PM": ["OS1 G04", "OS2 G05", "OS3 G06", "ML 108"], "03:15 PM - 04:15 PM": ["ADSA1 G04", "ES LAB 114/102", "ADSA3 G05", "DBMS2 G06"], "04:30 PM - 05:30 PM": ["RANAC1 G08", "ES LAB 114/102", "PC3 B05", "ADSA2 Lab 103"], "05:30 PM - 06:30 PM": ["ADSA2 Lab 103"]},
    "Wednesday": {"08:45 AM - 09:45 AM": ["ADSA2 G04", "CS G05", "DBMS3 G06"], "09:45 AM - 10:45 AM": ["ML 108", "PC4 B05", "OS2 G05"], "11:00 AM - 12:00 PM": ["ADSA1 G06", "ADSA3 LAB 103", "RANAC4 G07"], "12:00 PM - 01:00 PM": ["OOP1 G04", "ADSA3 LAB 103"], "02:15 PM - 03:15 PM": ["OOP4 G08", "OOP3 G06", "OOP1 Lab 103"], "03:15 PM - 04:15 PM": ["RANAC2 G04", "OOP1 Lab 103", "ES G07"], "04:30 PM - 05:30 PM": ["DBMS3 LAB 103", "PC1 Lab B05"], "05:30 PM - 06:30 PM": ["DBMS3 LAB 103", "PC1 Lab B05"]},
    "Thursday": {"08:45 AM - 09:45 AM": ["RANAC1 G09", "RANAC4 G06", "PC3 G07"], "09:45 AM - 10:45 AM": ["CNA G06", "OOP2 G08"], "11:00 AM - 12:00 PM": ["DBMS1 G06", "CNA Lab 114/102", "RANAC3 G05"], "12:00 PM - 01:00 PM": ["CNA Lab 114/102", "OS1 G04", "OS2 G05", "ML 111"], "02:15 PM - 03:15 PM": ["OOP4 Lab 103", "OOP3 G05"], "03:15 PM - 04:15 PM": ["PC1 B05", "OS3 G08", "RANAC2 G04", "OOP4 Lab 103"], "04:30 PM - 05:30 PM": ["DBMS2 LAB 103", "CS G09", "DBMS3 G06", "OOP1 G04"], "05:30 PM - 06:30 PM": ["DBMS2 LAB 103"]},
    "Friday": {"08:45 AM - 09:45 AM": ["RANAC3 G05", "PC4 Lab B05", "ADSA1 LAB 103"], "09:45 AM - 10:45 AM": ["ADSA1 LAB 103", "PC4 Lab B05", "OS3 B04"], "11:00 AM - 12:00 PM": ["DBMS2 G06", "OS1 G07", "ES B03"], "12:00 PM - 01:00 PM": ["PC2 B04", "ADSA3 G08"], "02:15 PM - 03:15 PM": ["RANAC1 G04", "ES G06", "ADSA2 G07"], "03:15 PM - 04:15 PM": ["DBMS1 LAB 103", "OOP3 G05", "OOP2 G06", "RANAC4 G04"], "04:30 PM - 05:30 PM": ["DBMS1 LAB 103", "PC2 Lab B05"], "05:30 PM - 06:30 PM": ["PC2 Lab B05"]},
    "Saturday": {}
}

raw_ug3 = {
    "Monday": {"08:45 AM - 09:45 AM": ["ICS 110", "BTA 111", "EP 105"], "09:45 AM - 10:45 AM": ["FDFED2 G05"], "11:00 AM - 12:00 PM": ["ML1 109", "ML2 110", "CD 111", "FQC 112", "PDS 108", "DSP G04"], "12:00 PM - 01:00 PM": ["AEM 105", "MML 110", "DE 111", "ASM 112", "MCD 108"], "02:15 PM - 03:15 PM": ["FDFED1 G06", "MPMC 108"], "03:15 PM - 04:15 PM": ["FDFED1 G06", "OS 109", "VLSI G09"], "04:30 PM - 05:30 PM": ["EP 108", "IDHV 112"]},
    "Tuesday": {"08:45 AM - 09:45 AM": ["ML1 109", "ML2 110", "FQC 112", "MCD 108", "CD 105", "OS 111"], "09:45 AM - 10:45 AM": ["DE 111", "PR 108", "ASM 104"], "11:00 AM - 12:00 PM": ["IR 109", "CC 110", "HPC 111", "NLP 108", "MPMC 105", "GDIT 112"], "12:00 PM - 01:00 PM": ["ICPS 105", "IDA G05"], "02:15 PM - 03:15 PM": ["FDFED2 G07", "DSP G08", "PDS 110"], "03:15 PM - 04:15 PM": ["FDFED2 G07"], "04:30 PM - 05:30 PM": ["BDA 109", "VLSI G04", "DIP 112"]},
    "Wednesday": {"08:45 AM - 09:45 AM": ["IR 109", "CC 110", "HPC 111", "GDIT 112", "NLP 108"], "09:45 AM - 10:45 AM": ["IDHV 112", "VLSI G09", "MML 110"], "11:00 AM - 12:00 PM": ["FDFED3 G05", "OS 110"], "12:00 PM - 01:00 PM": ["FDFED3 G05", "PDS 104"], "02:15 PM - 03:15 PM": ["ICPS 105", "IDA G05"], "03:15 PM - 04:15 PM": ["ML1 109", "ML2 110", "CD 111", "FQC 112", "MCD 105"]},
    "Thursday": {"08:45 AM - 09:45 AM": ["AEM 109", "DE 111"], "09:45 AM - 10:45 AM": ["IoTA 108", "ICS 110", "BTA 111", "DIP 112"], "11:00 AM - 12:00 PM": ["FDFED1 G04", "EP 110"], "12:00 PM - 01:00 PM": ["BDA 109", "PR 108"], "02:15 PM - 03:15 PM": ["IR 109", "CC 110", "HPC 111", "GDIT 112", "NLP 108"], "03:15 PM - 04:15 PM": ["FDFED3 G05", "DSP G06", "OS 109"], "04:30 PM - 05:30 PM": ["IoTA 109", "ICS 110", "BTA 111", "DIP 112"]},
    "Friday": {"08:45 AM - 09:45 AM": ["DSP G06", "IoTA 108", "BDA 109"], "09:45 AM - 10:45 AM": ["IDHV 112", "VLSI G04", "MML 110"], "11:00 AM - 12:00 PM": ["FDFED1 Lab G04", "FDFED2 Lab 103", "FDFED3 Lab G05", "MPMC Lab 114/104", "PDS 109"], "12:00 PM - 01:00 PM": ["FDFED1 Lab G04", "FDFED2 Lab 103", "FDFED3 Lab G05", "MPMC Lab 114/104"], "02:15 PM - 03:15 PM": ["ICPS 105", "IDA G05"], "03:15 PM - 04:15 PM": ["AEM 109", "ASM 112", "PR 108"], "04:30 PM - 05:30 PM": ["QRA 1 G09", "GENAI 110"]},
    "Saturday": {"08:45 AM - 09:45 AM": ["QRA 2 G09", "PGP2 G07"], "09:45 AM - 10:45 AM": ["QRA 2 G09", "PGP2 G07"], "11:00 AM - 12:00 PM": ["QRA 4 G09", "SE2 G08", "PGP1 G07", "SE1 G06"], "12:00 PM - 01:00 PM": ["QRA 4 G09", "SE2 G08", "PGP1 G07", "SE1 G06"], "02:15 PM - 03:15 PM": ["QRA 3 G09", "GENAI 105"], "03:15 PM - 04:15 PM": ["QRA 3 G09", "GENAI 105"]}
}

raw_ug4 = {
    "Monday": {"09:45 AM - 10:45 AM": ["VAR 108", "GNN-AI 105"], "02:15 PM - 03:15 PM": ["CRYPTO 110"], "03:15 PM - 04:15 PM": ["ANN 111", "RI 105"], "04:30 PM - 05:30 PM": ["DSD 105", "AE 104"]},
    "Tuesday": {"09:45 AM - 10:45 AM": ["GNN-AI 105", "ADL 109"], "12:00 PM - 01:00 PM": ["IDA G05"], "02:15 PM - 03:15 PM": ["DTCA 112", "ANN 111", "DL&CV 109"], "03:15 PM - 04:15 PM": ["CRYPTO 104"], "04:30 PM - 05:30 PM": ["BDA 109"]},
    "Wednesday": {"09:45 AM - 10:45 AM": ["DSD 105", "CRYPTO 104"], "11:00 AM - 12:00 PM": ["ADL 109", "VAR 108", "GNN-AI 105"], "12:00 PM - 01:00 PM": ["AE 110"], "02:15 PM - 03:15 PM": ["DTCA 112", "IDA G05", "DL&CV 109"], "03:15 PM - 04:15 PM": ["RI 108"]},
    "Thursday": {"09:45 AM - 10:45 AM": ["DSD 105", "ADL 109"], "11:00 AM - 12:00 PM": ["AE 104"], "12:00 PM - 01:00 PM": ["BDA 109"], "02:15 PM - 03:15 PM": ["DTCA 105"]},
    "Friday": {"08:45 AM - 09:45 AM": ["BDA 109"], "09:45 AM - 10:45 AM": ["VAR 108"], "11:00 AM - 12:00 PM": ["ANN 111", "DL&CV 104", "RI 105"], "02:15 PM - 03:15 PM": ["IDA G05"], "04:30 PM - 05:30 PM": ["GENAI 110"]},
    "Saturday": {"08:45 AM - 09:45 AM": ["OB1 B03"], "09:45 AM - 10:45 AM": ["OB1 B03"], "11:00 AM - 12:00 PM": ["OB2 B03"], "12:00 PM - 01:00 PM": ["OB2 B03"], "02:15 PM - 03:15 PM": ["GENAI"], "03:15 PM - 04:15 PM": ["GENAI"]}
}

def extract_rooms(raw_dict):
    parsed = {}
    for day, timeslots in raw_dict.items():
        parsed[day] = {}
        for time, classes in timeslots.items():
            parsed[day][time] = []
            for c in classes:
                # Targeted Room Extraction
                parts = c.split()
                if len(parts) > 1 and parts[-1].upper() not in ["114/102", "114/104"]:
                    if parts[-2].upper() == "LAB": room = parts[-2] + " " + parts[-1]
                    elif parts[-2].upper() == "B05" and parts[-3].upper() == "LAB": room = "Lab B05"
                    else: room = parts[-1]
                elif parts[-1].upper() in ["114/102", "114/104"]:
                    if len(parts) > 2 and parts[-2].upper() == "LAB": room = parts[-2] + " " + parts[-1]
                    else: room = parts[-1]
                else:
                    room = c 
                
                # Enforce precise naming for specific outlier labs
                if "ES LAB 114/102" in c: room = "LAB 114/102"
                elif "Lab B05" in c: room = "Lab B05"
                elif "LAB 103" in c or "Lab 103" in c: room = "LAB 103"
                elif "Lab G04" in c: room = "Lab G04"
                elif "Lab G05" in c: room = "Lab G05"
                elif "Lab 114/104" in c: room = "Lab 114/104"
                elif "Lab 114/102" in c: room = "Lab 114/102"
                
                parsed[day][time].append({"room": room})
    return parsed

timetable_db = {
    "UG1": perfect_ug1,
    "UG2": extract_rooms(raw_ug2),
    "UG3": extract_rooms(raw_ug3),
    "UG4": extract_rooms(raw_ug4)
}

with open('timetable.json', 'w') as f:
    json.dump(timetable_db, f, indent=4)
print("✅ Successfully generated timetable.json (Flawless Hardcoded Version)")