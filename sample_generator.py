import os
import sys

# Official VIGNAN R22 Academic Regulations & Supplementary Guidelines Dataset
VIGNAN_R22_PAGES = [
    {
        "page_number": 1,
        "title": "VIGNAN'S Foundation for Science, Technology & Research - Cover Page",
        "category": "Academic Regulations",
        "text": "VIGNAN'S Foundation for Science, Technology & Research (Deemed to be UNIVERSITY u/s 3 of UGC Act 1956). R22 Academic Regulations In Compliance with NEP 2020 for 4-Year B.Tech. Degree Programme."
    },
    {
        "page_number": 3,
        "title": "PREFACE by Vice Chancellor Prof. P. Nagabhushan",
        "category": "Academic Regulations",
        "text": "PREFACE: 'You are born to Blossom' - APJ Abdul Kalam and Arun K Tiwari. The doctrine of VIGNAN entitled R-22 contains the principles of policies laid down by the University to realize the spirit of 'Blossoming the lives'. R-22 document articulates the Academic Regulations of the University in force from academic year 2022-23. R-22 eliminates the melancholy of examinations, replacing high-stakes breakdown with continuous assessment. Prof. P. NAGABHUSHAN, Vice Chancellor, VFSTR."
    },
    {
        "page_number": 7,
        "title": "Executive Abstract & Salient Features",
        "category": "Academic Regulations",
        "text": "Executive Abstract: R22 Academic regulations, Curriculum and course contents is an articulation of VFSTR's commitment towards NEP-2020. The proposed framework accomplishes multi-disciplinary holistic education, continuous assessment along with multiple honorable exit options if a student falls short to complete requirements within the stipulated period. B.Tech degree is 4 years (8 semesters) duration with lateral entry and exit options. Salient Features: Multidisciplinary, Continuous learning & assessment (60% weightage), Honours / Research Honours / Minor / Add-on Diploma options (+20 credits), Lateral entry and exit options (Exit at 120 credits with Engineering Diploma or B.Sc.), Sabbatical Semester Drop option, Dual B.Tech + M.Tech / MBA degree of 5 years, Credit transfer."
    },
    {
        "page_number": 8,
        "title": "1.1 Definitions - Degree, Course, Semester Drop, Supplementary",
        "category": "Academic Regulations",
        "text": "1.1 Definitions: 'Degree' refers to B.Tech Degree Program. 'Course' refers to paper/subject for which student earns credits after assessment. Project is treated as a Course. 'Continuous Assessment' refers to student evaluation spread over the entire semester. 'Semester' refers to a period covering Formative and Summative Assessment periods (generally 20 weeks). 'Course Drop' refers to repeat of course(s) due to failing credit requirements. 'Supplementary Examinations' refers to examinations conducted to allow students to clear un-cleared semester-end summative assessment. 'Blank Semester / Semester Drop' refers to a semester where student drops all courses or takes sabbatical for creative extension activity."
    },
    {
        "page_number": 10,
        "title": "1.3 Program Duration & 1.4 Courses & Credits System",
        "category": "Academic Regulations",
        "text": "1.3 Program Duration: Normal duration to complete B.Tech program is 4 years (8 semesters). Maximum duration (spill over period) allowed is 7 years (14 semesters). 1.4 Courses and Credits: 1 hour Lecture (L) per week = 1 Credit. 2 hours Practical (P) per week = 1 Credit. 2 hours Tutorial (T) per week = 1 Credit. Total Credits for Regular B.Tech = 161 Credits. B.Tech with Honours / Minors = 161 + 20 Add-on Credits = 181 Credits (Requires minimum CGPA of 8.0 up to 4th semester)."
    },
    {
        "page_number": 13,
        "title": "2.1 Credit Distribution across Course Categories (161 Total)",
        "category": "Academic Regulations",
        "text": "2.1 Distribution of Credits: Total 161 Credits distributed as follows: Professional Core = 53 Credits (32.92%), Electives (Dept & Open) = 34 Credits (21.12%), Basic Engineering = 20 Credits (12.42%), Humanities and Management = 15 Credits (09.32%), Basic Sciences = 19 Credits (11.80%), Life Skills / Physical Fitness = 6 Credits (03.72%), Projects = 14 Credits (08.70%). Total = 161 Credits (100%)."
    },
    {
        "page_number": 16,
        "title": "4. ATTENDANCE REGULATIONS & Condonation Rules",
        "category": "Attendance Policy",
        "text": "4. ATTENDANCE REGULATIONS: Mandatory Attendance: VFSTR expects 100% attendance. However, attendance in each course shall NOT be less than 75% of aggregate of all L, T, P sessions conducted in that course. Attendance calculation is reviewed every 4 weeks and finalized at 15th week. Attendance Shortage Condonation (Up to 10%): Shortage of attendance between 65% and 74% may be condoned up to 10% on grounds of: a) Ill-health (medical emergency supported by hospital medical certificate), b) Social obligations or representing VFSTR in sports/cultural events, c) Placement activities. Medical reports must be submitted on time for scrutiny by Vice-Chancellor committee. Consequence of Shortage (< 65% or uncondoned): Candidate is awarded 'R' (Repeat) Grade, BARRED from semester-end summative assessment, and MUST re-register during summer semester or regular semesters."
    },
    {
        "page_number": 17,
        "title": "5. ASSESSMENT SCHEME - 60% Formative + 40% Summative",
        "category": "Examination Guidelines",
        "text": "5. ASSESSMENT SCHEME: Marks Distribution: Maximum sum of Formative and Summative assessment marks is 100, in 60:40 ratio (60% Formative Assessment + 40% Summative Assessment). Qualifying Criteria: To pass a course, student must secure at least Grade 4.0 out of 10 after relative grading. Minimum 35% in Formative Assessment (21 out of 60 marks) AND minimum 35% in Summative Assessment (14 out of 40 marks) individually. If formative marks < 21/60, candidate gets 'R' grade. If summative marks < 14/40, candidate gets 'I' (Incomplete) grade."
    },
    {
        "page_number": 18,
        "title": "5.3 Formative Assessment Targets T1, T2, T3, T4, T5 (60 Marks)",
        "category": "Examination Guidelines",
        "text": "5.3 Formative Assessment Targets (60 Marks total across 5 targets per module): T1 Classroom Test (10 Marks): 60 min written test. Part A (Module bank problem) + Part B (Unseen application problem). T2 Extension & Validation (10 Marks): Simulation/Case study extension. T3 Technical Report & Voice PPT (10 Marks): IEEE/APA report presentation. T4 Online MCQ Test (10 Marks): 20 Shuffled online MCQs (30 mins). T5 Continuous Lab Practice CLPA (20 Marks): Minimum 4 lab practice assignments @ 5 marks each."
    },
    {
        "page_number": 27,
        "title": "7. COMPUTATION OF GRADING - Relative Grading System",
        "category": "Academic Regulations",
        "text": "7. COMPUTATION OF RELATIVE GRADING: Relative grade point P = (m / Th) * 10 [limited to 10], where m = total marks (formative + summative) and Th = threshold upper bound. Letter Grades Table: Grade O (Outstanding, P >= 9.50), Grade S (Excellent, P >= 8.50 to 9.49), Grade A (Very Good, P >= 7.00 to 8.49), Grade B (Good, P >= 6.00 to 6.99), Grade C (Fair, P >= 5.00 to 5.99), Grade M (Marginal Pass, P >= 4.00 to 4.99), Grade R (Transitional Repeat), Grade I (Transitional Incomplete)."
    },
    {
        "page_number": 28,
        "title": "9. GRADE POINT AVERAGE - SGPA & CGPA Formulas",
        "category": "Academic Regulations",
        "text": "9. GRADE POINT AVERAGE: SGPA Formula: SGPA = Sum(C_i * P_i) / Sum(C_i) for all courses i in the semester, where P_i is grade points and C_i is credits. CGPA Formula: CGPA = Sum(C_j * P_j) / Sum(C_j) for all courses j across the entire program. Percentage Equivalence: Percentage = CGPA * 10."
    },
    {
        "page_number": 29,
        "title": "10. AWARD OF CLASS & Degree Conferment Requirements",
        "category": "Academic Regulations",
        "text": "10. AWARD OF CLASS: CGPA >= 7.00 = First Class with Distinction. CGPA 6.00 to 6.99 = First Class. CGPA 5.00 to 5.99 = Second Class. CGPA 4.00 to 4.99 = Pass Class. CGPA < 4.00 = Incomplete. Degree Requirements: Bonafide student for 4 to 7 years, completed 161 credits, cleared No Dues from Library/Hostel/Finance, and no pending disciplinary/ragging cases."
    },
    {
        "page_number": 30,
        "title": "12. LATERAL EXIT OPTIONS & 13. CHANGE OF BRANCH",
        "category": "Academic Regulations",
        "text": "12.3 Honorable Exit Option (NEP 2020): Student completing 6 semesters and minimum 120 credits can exit with Engineering Diploma or B.Sc. degree. Can re-enter within 7 years to complete B.Tech by surrendering Diploma/B.Sc. 13. Change of Branch Discipline: Allowed after 1st year (2 semesters). Top 1% students in each branch based on CGPA eligible. Must have cleared all 1st year credit requirements."
    }
]

EXAM_GUIDELINES_PAGES = [
    {
        "page_number": 1,
        "title": "VFSTR Examination & Evaluation Guidelines",
        "category": "Examination Guidelines",
        "text": "1. Hall Ticket Eligibility: Online hall tickets released 5 days before exams. Requirements: Minimum 75% attendance, no-dues clearance, and regular exam registration. 2. Exam Timings: Morning session 09:30 AM - 12:30 PM (Late entry up to 09:45 AM). Afternoon session 01:30 PM - 04:30 PM. 3. Malpractice Penalties: Carrying mobile phones or cheat sheets leads to exam cancellation and 'R' grade. Impersonation leads to 1-2 years expulsion. 4. Revaluation Fee: Rs 500 for Recounting, Rs 1500 for Revaluation within 10 days of results."
    }
]

STUDENT_HANDBOOK_PAGES = [
    {
        "page_number": 1,
        "title": "VFSTR Student Handbook & Campus Code of Conduct",
        "category": "Student Handbook",
        "text": "1. Campus Code of Conduct: ID card mandatory at all times. Formal dress code enforced. Zero tolerance for alcohol, tobacco, or illegal substances. 2. Anti-Ragging Policy: Zero tolerance under UGC directives. Helpline: 1800-180-5522. Punishment: Immediate FIR, suspension, and expulsion. 3. Hostel Rules: Curfew at 06:30 PM for Girls and 07:30 PM for Boys. Out-pass required. 4. Library Hours: 08:00 AM to 10:00 PM."
    }
]

def load_preloaded_university_dataset():
    all_pages = []
    
    # Process VIGNAN R22 Academic Regulations
    for item in VIGNAN_R22_PAGES:
        all_pages.append({
            "doc_id": "vignan_r22_academic_regulations",
            "doc_name": "VIGNAN_R22_Academic_Regulations.pdf",
            "page_number": item["page_number"],
            "total_pages": 40,
            "category": item["category"],
            "section": item["title"],
            "raw_text": item["text"],
            "cleaned_text": item["text"]
        })
        
    for item in EXAM_GUIDELINES_PAGES:
        all_pages.append({
            "doc_id": "examination_guidelines",
            "doc_name": "Examination_Guidelines.pdf",
            "page_number": item["page_number"],
            "total_pages": 5,
            "category": item["category"],
            "section": item["title"],
            "raw_text": item["text"],
            "cleaned_text": item["text"]
        })

    for item in STUDENT_HANDBOOK_PAGES:
        all_pages.append({
            "doc_id": "student_handbook",
            "doc_name": "Student_Handbook.pdf",
            "page_number": item["page_number"],
            "total_pages": 8,
            "category": item["category"],
            "section": item["title"],
            "raw_text": item["text"],
            "cleaned_text": item["text"]
        })

    return all_pages

def generate_all_samples(base_dir="data"):
    os.makedirs(base_dir, exist_ok=True)
    print("Sample dataset initialized successfully.")

if __name__ == "__main__":
    generate_all_samples()
