import sqlite3
import pandas as pd


conn = sqlite3.connect("university.db")

c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT default NULL,
    email TEXT NOT NULL UNIQUE,

    full_name TEXT NOT NULL,
    program TEXT NOT NULL,
    specialization TEXT,
    semester_enrolled TEXT NOT NULL,

    gpa REAL,
    credits_completed INTEGER DEFAULT 0
)
""")

c.execute("""
INSERT INTO students (id, username, email, full_name, program, specialization, gpa, semester_enrolled, credits_completed) VALUES (1, 'lea07','hyunjuji0819@gmail.com','Lea Ji', 'ms-cs', 'Machine Learning', 4.0, 'Fall 2024', 15),
(2, 'woohyun12','ji819kr@gmail.com','Woohyun Noh', 'ms-cs', 'Robotics', 4.0, 'Fall 2024', 18)
""")

conn.commit()

c.execute("""
CREATE TABLE transcripts (
id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id INTEGER NOT NULL,
offering_id INTEGER NOT NULL,
grade TEXT NOT NULL,

FOREIGN KEY (student_id) REFERENCES students(id),
FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id)
)
""")


c.execute("""
INSERT INTO transcripts (student_id, offering_id, grade) VALUES (1, 1, 'A'),
(1, 2, 'A'),
(1, 3, 'A'),
(1, 6, 'A'),
(1, 7, 'A'),
(2, 1, 'A'),
(2, 4, 'A'),
(2, 5, 'A'),
(2, 8, 'A'),
(2, 9, 'A'),
(2, 10, 'A')
""")

c.execute("""
CREATE TABLE IF NOT EXISTS professors (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    affiliation TEXT NOT NULL,
    title TEXT NOT NULL,
    office TEXT
)
""")

professors = [
    (1, "mahdir", "Mahdi Roozbahani", "School of Computational Science and Engineering", "lecturer", None),
    (2, "john.stasko", "John Stasko", "School of Interactive Computing", "Professor", "TSRB 355"),
    (3, "varma", "Sashank Varma", "School of Interactive Computing", "Professor", None),
    (4, "hays", "James Hays", "School of Interactive Computing", "Associate Professor", "CODA 11th floor"),
    (5, "ashok.goel", "Ashok Goel", "School of Computational Science and Engineering", "Professor", None),
    (6, "matthew.gombolay", "Matthew Gombolay", "School of Interactive Computing", "Associate Professor", None),
    (7, "sehoonha", "Sehoon Ha", "School of Interactive Computing", "Assistant Professor", "Klaus 3226"),
    (8, "ssingla7", "Sahil Singla", "School of Computer Science", "Assistant Professor", "Klaus 2142"),
    (9, "harish.ravichandar", "Harish Ravichandar", "School of Interactive Computing", "Assistant Professor", None),
    (10, "shi", "Humphrey Shi", "School of Interactive Computing", "Associate Professor", None),
    (11, "chernova", "Sonia Chernova", "School of Interactive Computing", "Associate Professor", None),
    (12, "thomas.ploetz", "Thomas Ploetz", "School of Interactive Computing", "Professor", None),
    (13, "wei.xu", "Wei Xu", "School of Interactive Computing", "Associate Professor", None),
    (14, "nimam6", "Nabil Imam", "School of Computational Science and Engineering", "Assistant Professor", None),
    (15, "danfei", "Danfei Xu", "School of Interactive Computing", "Assistant Professor", None),
    (16, "wenke.lee", "Wenke Lee", "School of Computer Science", "Professor", None)
]

c.executemany("""
INSERT INTO professors (id, username, full_name, affiliation, title, office)
VALUES (?, ?, ?, ?, ?, ?)
""", professors)

c.execute("""
CREATE TABLE IF NOT EXISTS courses (
    course_id TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    department TEXT NOT NULL,
    credits INTEGER NOT NULL,
    description TEXT
)
""")

courses = {
    "CS6515": ("CS6515", "Introduction to Graduate Algorithms", "Computer Science", 3,
               "Advanced study of algorithm design and analysis techniques."),
    "CS7496": ("CS7496", "Computer Animation", "Computer Science", 3,
               "Introduction to computer animation techniques and applications."),
    "CS7633": ("CS7633", "Human-Robot Interaction", "Computer Science", 3,
               "Human-robot interaction and collaboration."),
    "CS7631": ("CS7631", "Multi-Robot Systems", "Computer Science", 3,
               "Multi-robot systems and their applications."),
    "CS6601": ("CS6601", "Artificial Intelligence", "Computer Science", 3,
               "Introduction to artificial intelligence concepts and techniques."),
    "CS7641": ("CS7641", "Machine Learning", "Computer Science", 3,
               "Introduction to machine learning algorithms and applications."),
    "CS7651": ("CS7651", "Human and Machine Learning", "Computer Science", 3,
               "Fundamentals of human and machine learning in cognitive science view."),
    "CS6730": ("CS6730", "Data Visualization Principles", "Computer Science", 3,
               "Principles and techniques for effective data visualization."),
    "CS7637": ("CS7637", "Knowledge-Based AI", "Computer Science", 3,
               "Introduction to knowledge-based AI systems and applications."),
    "CS7650": ("CS7650", "Natural Language", "Computer Science", 3,
               "Introduction to natural language processing and understanding."),
    "CSE6140": ("CSE6140", "Computational Science and Engineering Algorithms", "Computational Science and Engineering", 3,
               "Introduction to computational science and engineering algorithms."),
    "CS7643": ("CS7643", "Deep Learning", "Computer Science", 3,
               "Introduction to deep learning and neural networks."),
    "CS8803-DRL": ("CS8803-DRL", "Deep Reinforcement Learning", "Computer Science", 3,
               "Introduction to deep reinforcement learning techniques and applications."),
    "CS7648": ("CS7648", "Interactive Robo Learn", "Computer Science", 3,
               "Introduction to interactive robot learning techniques and applications."),
    "CS6476": ("CS6476", "Computer Vision", "Computer Science", 3,
               "Computer vision techniques and applications."),
    "CS6035": ("CS6035", "Intro To Info Security", "Computer Science", 3,
               "Introduction to information security concepts and techniques."),
}

c.executemany("""
INSERT OR IGNORE INTO courses (course_id, course_name, department, credits, description)
VALUES (?, ?, ?, ?, ?)
""", courses.values())

c.execute("""
CREATE TABLE IF NOT EXISTS course_offerings (
    offering_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT NOT NULL,
    professor_id INTEGER NOT NULL,
    semester TEXT NOT NULL,
    schedule TEXT,
    location TEXT,
    max_students INTEGER,
    enrolled_students INTEGER,

    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (professor_id) REFERENCES professors(id)
)
""")


course_offerings = [
    ("CS7641", 1, "Fall 2024", "Mon/Wed 12:30 - 13:45", "Scheller College of Business 100", 315, 315),
    ("CS7651", 3, "Fall 2024", "Tue/Thu 17:00 - 18:15", "Scheller College of Business 202", 50, 49),
    ("CS6730", 2, "Fall 2024", "Tue/Thu 14:00 - 15:15", "Instructional Center 211", 110, 100),
    ("CS7496", 7, "Fall 2024", "Mon/Wed/Fri 11:00 - 11:50", "Scheller College of Business 300", 42, 41),
    ("CS6476", 10, "Fall 2024", "Tue/Thu 11:00 - 12:15", "College of Computing 16", 239, 239),

    ("CS6476", 4, "Spring 2025", "Mon/Wed 15:30 - 16:45", "College of Computing 16", 250, 246),
    ("CS7637", 5, "Spring 2025", "Mon/Wed 14:00 - 15:15", "Scheller College of Business 300", 76, 73),
    ("CS7648", 6, "Spring 2025", "Mon/Wed 09:30 - 10:45", "Skiles 254", 30, 26),
    ("CS8803-DRL", 7, "Spring 2025", "Tue/Thu 11:00 - 12:15", "Molecular Sciences and Engr G011", 150, 136),
    ("CS7631", 9, "Spring 2025", "Mon/Wed 14:00 - 15:15", "Scheller College of Business 223", 50, 48),

    ("CS6515", 8, "Fall 2025", "Tue/Thu 15:30 - 16:45", "Clough UG Learning Commons 152", 180, 150),
    ("CS7633", 11, "Fall 2025", "Mon/Wed 14:00 - 15:15", "Instructional Center 109", 60, 48),
    ("CS6601", 12, "Fall 2025", "Tue/Thu 14:00 - 15:15", "Howey Physics L1", 240, 160),
    ("CS7650", 13, "Fall 2025", "Mon/Wed 14:00 - 15:15", "Howey Physics L3", 130, 129),
    ("CSE6140", 14, "Fall 2025", "Mon/Wed 11:00 - 12:15", "Paper Tricentennial 109", 25, 20),
    ("CS7643", 15, "Fall 2025", "Mon/Wed 15:30 - 16:45", "Clough UG Learning Commons 144", 150, 149),
    ("CS6035", 16, "Fall 2025", "Tue/Thu 14:00 - 15:15", "Scheller College of Business 300", 120, 18)
]


c.executemany("""
INSERT INTO course_offerings (course_id, professor_id, semester, schedule, location, max_students, enrolled_students)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", course_offerings)

# df = pd.read_sql_query("SELECT * FROM students", conn)
# print(df)

# df = pd.read_sql_query("SELECT * FROM transcripts", conn)
# print(df)

# df = pd.read_sql_query("SELECT * FROM professors", conn)
# print(df)

# df = pd.read_sql_query("SELECT * FROM courses", conn)
# print(df)

# df = pd.read_sql_query("SELECT * FROM course_offerings", conn)
# print(df)

# df = pd.read_sql_query("""
# SELECT c.*
# FROM courses c
# JOIN course_offerings co ON c.course_id = co.course_id
# JOIN transcripts t ON co.offering_id = t.offering_id
# JOIN students s ON t.student_id = s.id
# WHERE s.full_name = 'Lea Ji'
# """, conn)
# print(df)

conn.commit()
conn.close()