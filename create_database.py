"""
WATRANA RAG System - Database Setup Script
Yeh script SQLite database banata hai aur sample data insert karta hai.
Run: python create_database.py
"""

import sqlite3
import os

DB_PATH = "data/watrana.db"

# Sample problems from last 20 years (industrial/manufacturing domain)
SAMPLE_DATA = [
    {
        "year": 2004,
        "category": "Mechanical",
        "problem": "Conveyor belt ka belt slip ho raha tha aur production band ho gayi",
        "cause": "Belt tension kam thi aur pulley worn out thi",
        "solution": "Belt tension 15% badhaya, pulley replace ki, alignment check kiya. Har 3 mahine mein preventive maintenance schedule banaya.",
        "downtime_hours": 8,
        "department": "Production"
    },
    {
        "year": 2005,
        "category": "Electrical",
        "problem": "Motor overheating ki wajah se machine shut down ho rahi thi",
        "cause": "Cooling fan dusty tha aur ambient temperature zyada thi",
        "solution": "Cooling fan clean kiya, motor insulation check ki, temperature sensor calibrate kiya. Monthly cleaning schedule banaya.",
        "downtime_hours": 4,
        "department": "Maintenance"
    },
    {
        "year": 2006,
        "category": "Hydraulic",
        "problem": "Hydraulic press mein oil leak ho raha tha",
        "cause": "O-ring worn out thi aur pressure relief valve faulty thi",
        "solution": "O-rings replace ki, pressure relief valve change kiya, oil level maintain kiya. 6 mahine mein seal inspection schedule banaya.",
        "downtime_hours": 12,
        "department": "Production"
    },
    {
        "year": 2007,
        "category": "Quality",
        "problem": "Product ka weight inconsistent aa raha tha - specification se bahar",
        "cause": "Weighing sensor calibration drift aur raw material variation",
        "solution": "Sensor daily calibrate karna shuru kiya, supplier se raw material specification tighten ki. Statistical process control implement kiya.",
        "downtime_hours": 6,
        "department": "Quality Control"
    },
    {
        "year": 2008,
        "category": "Pneumatic",
        "problem": "Pneumatic cylinder stroke complete nahi kar raha tha",
        "cause": "Air pressure insufficient tha aur cylinder seals damaged thi",
        "solution": "Compressor pressure 6 bar se 8 bar kiya, cylinder seals replace ki, air filter clean kiya.",
        "downtime_hours": 5,
        "department": "Production"
    },
    {
        "year": 2009,
        "category": "Electrical",
        "problem": "PLC program crash ho gaya aur production line ruk gayi",
        "cause": "Power fluctuation se PLC memory corrupt ho gaya",
        "solution": "PLC program backup se restore kiya, UPS install kiya, voltage stabilizer lagaya. Weekly backup procedure banaya.",
        "downtime_hours": 16,
        "department": "Automation"
    },
    {
        "year": 2010,
        "category": "Mechanical",
        "problem": "Gearbox se unusual noise aa raha tha aur vibration zyada thi",
        "cause": "Bearing wear out ho gaya tha aur lubrication insufficient thi",
        "solution": "Bearing replace kiya, lubrication schedule update kiya, alignment realign kiya. Vibration monitoring sensor lagaya.",
        "downtime_hours": 10,
        "department": "Maintenance"
    },
    {
        "year": 2011,
        "category": "Quality",
        "problem": "Finished product mein surface defects aa rahe the",
        "cause": "Tooling wear aur cutting speed incorrect thi",
        "solution": "Tool life monitoring system implement kiya, cutting parameters optimize kiye, inspection frequency badhaya.",
        "downtime_hours": 3,
        "department": "Quality Control"
    },
    {
        "year": 2012,
        "category": "Safety",
        "problem": "Worker ko minor injury aayi machine ke near-miss incident mein",
        "cause": "Safety guard missing thi aur operator training incomplete thi",
        "solution": "Safety guards install kiye, mandatory safety training shuru ki, incident reporting system banaya, PPE checklist implement kiya.",
        "downtime_hours": 24,
        "department": "Safety"
    },
    {
        "year": 2013,
        "category": "Electrical",
        "problem": "VFD drive trip ho raha tha randomly",
        "cause": "Loose connection aur earth fault thi",
        "solution": "All connections tight kiye, earthing improve kiya, cable routing properly kiya, periodic termination check schedule banaya.",
        "downtime_hours": 7,
        "department": "Electrical"
    },
    {
        "year": 2014,
        "category": "Mechanical",
        "problem": "Pump cavitation ki problem aa rahi thi",
        "cause": "Suction line mein air leak tha aur NPSH insufficient thi",
        "solution": "Suction line seals replace ki, pump speed optimize ki, inlet filter clean kiya, NPSH calculation review kiya.",
        "downtime_hours": 9,
        "department": "Utilities"
    },
    {
        "year": 2015,
        "category": "Quality",
        "problem": "Product ka color variation aa raha tha batch to batch",
        "cause": "Mixing time inconsistent tha aur colorant dosing incorrect tha",
        "solution": "Automated dosing system install kiya, mixing time standardize kiya, color measurement spectrophotometer se karna shuru kiya.",
        "downtime_hours": 2,
        "department": "Quality Control"
    },
    {
        "year": 2016,
        "category": "Automation",
        "problem": "Robot arm position accuracy kho rahi thi",
        "cause": "Servo motor encoder drift aur mechanical backlash",
        "solution": "Encoder recalibrate kiya, backlash compensation program update kiya, quarterly calibration schedule banaya.",
        "downtime_hours": 11,
        "department": "Automation"
    },
    {
        "year": 2017,
        "category": "Hydraulic",
        "problem": "Hydraulic cylinder drift kar raha tha position hold nahi ho raha",
        "cause": "Internal bypass valve worn out tha",
        "solution": "Control valve rebuild kiya, hydraulic fluid quality check kiya, contamination control improve kiya.",
        "downtime_hours": 8,
        "department": "Production"
    },
    {
        "year": 2018,
        "category": "Electrical",
        "problem": "Control panel mein overheating ho rahi thi",
        "cause": "Panel cooling inadequate tha aur components outdated the",
        "solution": "AC unit panel mein install kiya, cable management improve kiya, load distribution balance kiya.",
        "downtime_hours": 6,
        "department": "Electrical"
    },
    {
        "year": 2019,
        "category": "Mechanical",
        "problem": "Chain drive stretch ho gayi thi aur slipping thi",
        "cause": "Lubrication neglect aur overloading",
        "solution": "Chain replace ki, sprocket inspect kiya, automatic lubrication system install kiya, load limits define kiye.",
        "downtime_hours": 5,
        "department": "Production"
    },
    {
        "year": 2020,
        "category": "Safety",
        "problem": "Chemical spillage incident production floor par",
        "cause": "Container crack tha aur spill containment inadequate tha",
        "solution": "Spill containment bund banaya, chemical storage improve kiya, spill kit install kiya, emergency response training di.",
        "downtime_hours": 20,
        "department": "Safety"
    },
    {
        "year": 2021,
        "category": "Automation",
        "problem": "SCADA system data logging band ho gaya tha",
        "cause": "HMI hard disk full ho gaya tha aur database corrupt thi",
        "solution": "Cloud backup implement kiya, disk space monitoring lagaya, database maintenance schedule banaya, redundant storage add kiya.",
        "downtime_hours": 14,
        "department": "Automation"
    },
    {
        "year": 2022,
        "category": "Quality",
        "problem": "Dimension tolerance se bahar aa rahi thi machined parts ki",
        "cause": "CNC machine thermal expansion aur tool wear",
        "solution": "Thermal compensation feature enable kiya, tool wear monitoring implement kiya, in-process gauging install kiya.",
        "downtime_hours": 4,
        "department": "Quality Control"
    },
    {
        "year": 2023,
        "category": "Mechanical",
        "problem": "Cooling tower ki fill packing damaged ho gayi thi",
        "cause": "Water quality poor thi aur scale buildup tha",
        "solution": "Fill packing replace ki, water treatment chemical dosing optimize kiya, regular blowdown schedule banaya, water quality monitoring shuru kiya.",
        "downtime_hours": 18,
        "department": "Utilities"
    },
]


def create_database():
    """Database aur table banata hai"""
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table create karo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            category TEXT NOT NULL,
            problem TEXT NOT NULL,
            cause TEXT NOT NULL,
            solution TEXT NOT NULL,
            downtime_hours REAL DEFAULT 0,
            department TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check karo ki data already hai ya nahi
    cursor.execute("SELECT COUNT(*) FROM problems")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Sample data insert karo
        for item in SAMPLE_DATA:
            cursor.execute("""
                INSERT INTO problems (year, category, problem, cause, solution, downtime_hours, department)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item["year"], item["category"], item["problem"],
                item["cause"], item["solution"],
                item["downtime_hours"], item["department"]
            ))
        
        conn.commit()
        print(f"✅ Database created successfully!")
        print(f"✅ {len(SAMPLE_DATA)} sample records inserted!")
    else:
        print(f"ℹ️  Database already has {count} records. Skipping insert.")
    
    conn.close()
    print(f"📁 Database saved at: {DB_PATH}")


if __name__ == "__main__":
    create_database()
