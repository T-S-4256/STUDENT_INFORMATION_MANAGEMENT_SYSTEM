import pymongo
import logging
import os
import pandas as pd 
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# LOAD ENV DATA 
load_dotenv()
11

# FETCHING THE CURRENT PROJECT ABSOLUTE PATH
logFilePath = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "allLog", "Logs.log"
)

# CREATE FILE IN CASE IF FILE NOT EXIST
os.makedirs(os.path.dirname(logFilePath), exist_ok=True)

# LOGGING CONFIGRATION SET UP
logging.basicConfig(
    filename=logFilePath,
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


# DATABASE CONNECTION SET UP 
try:
    # CONNECT WITH DATABASE 
    Client=pymongo.MongoClient(os.environ.get("mongo_url"))
    # CREATE A DATABASE 
    S_I_M_S_DB=Client['S_I_M_S_Terminal']
    # CREATE A COLLECTION IN THE DATABSE 
    simsCollection=S_I_M_S_DB['student_info']
except Exception as e:
    logging.warning("Failed To Connect With MonogoDB")


# ***********************************************  ADD STUDENT FUNCTION *********************************************************
# DYNAMICALLY GENERATE THE ROLL NUMBER FOR EACH STUDENT 
def generate_roll():
    logging.info("Generate Roll Request Fetched")
    last_doc = simsCollection.find_one(sort=[("roll_number", -1)])
    last_roll = last_doc["roll_number"] if last_doc else "R02025100"
    last_num=int(last_roll[-3:])+1
    finel_roll="R02025"+str(last_num)
    logging.info(f"Roll Number Generated Successfully : {finel_roll}")
    return finel_roll

# ADD STUDENT FUNCTION 
def add_student():
    # SAVE THE LOG 
    logging.info("Add Student Request Fetched ")
    # FETCH ALL THE STUDENT INFORMATION AS INPUT 
    name=(input("Enter Student Name : ")).strip()
    roll_number=generate_roll()
    course=input("Enter Student Course : ").strip()
    dob=input("Enter Student Date OF Birth : ").strip()
    semester=input("Enter Student Semester : ").strip()
    
    # IF ANY OF THE DATA FOUND INVALID THEN 
    if len(name)==0 or len(roll_number)==0 or len(course)==0 or len(dob)==0 or len(semester)==0:
        # IF FOUND YES THEN SAVE THE LOG AND RETURN BACK
        logging.warning("Invalid Data Found ")
    else:
        # SAVE THE DATA OF THE STUDENT INTO THE DATABSE 
        try:
            updatedData=simsCollection.insert_one({"name":name,"course":course,"roll_number":roll_number,"date_of_birth":dob,"semester":semester,"grade":None,"marks":{}})
            logging.info(f"Student Added Successfully,Student Data : {updatedData}")
            print("Student Added Successfully!")
        except Exception as e:
            # SAVE THE LOG IN CASE FAIL TO ADD THE STUDENT 
            logging.error("Something Went Wrong During Adding Student")


# ****************************************************  DELETE STUDENT FUNCTION *************************************************

def delete_student():
    # SAVE THE LOG 
    logging.info("Delete Student Request Fetched")
    
    # TAKE USER DETAILS OF STUDENT TO DELETE 
    name=input("Enter Student Name : ").strip()
    roll_number=input("Enter Student Roll Number : ").strip()
    # IF ANY OF THE DATA FOUND INVALID 
    if len(name)==0 or len(roll_number)==0:
        # SAVE THE LOG AND RETURN BACK 
        logging.warning("Invalid Data Found")
    else:
        try:
            # DELETE THE STUDENT FROM THE DATABASE
            simsCollection.find_one_and_delete({"roll_number":roll_number,"name":name})
            # SAVE THE LOG 
            logging.info("Student Deleted Successfullt")
            print("Student Data Deleted Successfully!")
        except Exception as e:
            # IF ANY ERROR THEN SAVE THE ERROR LOG 
            logging.error("Error Occured During Deleteing Student")

# ******************************************** UPDATE THE STUDENT DETAILS ******************************************************
def update_student():
    # SAVE THE LOG 
    logging.info("Update Student Request Fetched ")
    
    # TAKE THE ROLL NUMBER WHOSE DATA HAVE TO UPDATE 
    roll_number=input("Enter Student Roll Number To Update Data : ")
    
    # FIND THE STUDENT IN THE DATABASE BASED ON ROLL NUMBER 
    try:
        student=simsCollection.find_one({"roll_number":roll_number})
        logging.info(f"Student Found : {student}")
    except Exception as e:
        logging.error("Error Occured In Finding Student")
    if student:
        # IF STUDENT FOUND THEN TAKE THE NEW DATA TO UPDATE 
        print("Enter The Details To Update : ")
        name=input("Enter Student Name : ").strip()
        course=input("Enter Student Course : ").strip()
        dob=input("Enter Student Date Of Birth : ").strip()
        semester=input("Enter Students Semester : ").strip()
        try:
            # UPADTE THE DATA IN THE DATABASE 
            updatedData=simsCollection.find_one_and_update({"roll_number":roll_number},{"$set":{"name":name,"course":course,"date_of_birth":dob,"semster":semester}},return_document=pymongo.ReturnDocument.AFTER)
            # SAVE THE LOG 
            logging.info(f"Student Data Updated Successfullt ,Updated Data : {updatedData}")
            
            print("Student Data Updated Successfully!")
        except Exception as e:
            logging.error("Error Occured In Updating Student Data")
    else:
        logging.warning("Invalid Roll Number")


# ****************************************** STORE MARKS OF THE STUDENT *****************************************

# CALCULATE GRADE 
def calculate_grade(marks):
    sum=0
    for i in marks:
        if i<30:
            return "Fail"
        else:
            sum+=i
    if sum>=400:
        return "Destination"
    elif sum>=300:
        return "Fisrt"
    elif sum>=250:
        return "Second"
    elif sum>=200:
        return "Third"
    else:
        return "Fail"

# STORE STUDENT MARKS 
def store_marks():
    # SAVE THE LOG 
    logging.info("Store Marks Request Fetched ")
    
    # TAKE THE ROLL NUMBER WHOSE MARKS I HAVE TO ADD 
    roll_number=input("Enter Student Roll Number : ").strip()
    
    # CHECK THE ROLL NUMBER IS VALID OR NOT 
    try:
        # FIND THE STUDENT 
        student =simsCollection.find_one({"roll_number":roll_number})
    except Exception as e:
        logging.error("Error Occured In Finding The Student For Adding Marks")
    
    if student:
        # FETCH THE MARKS FROM THE USER TO ADD THE MARKS OF THE STUDENT 
        try:
            semester=input("Which Semster Marks You Are Adding : ").strip()
            maths=int(input("Enter Marks Of Math Subject : ").strip())
            phy=int(input("Enter Marks Of Physics Subject : ").strip())
            chem=int(input("Enter Marks Of Chemistry Subject : ").strip())
            hindi=int(input("Enter Marks Of Hindi Subject : ").strip())
            english=int(input("Enter Marks Of English Subject : ").strip())
        except ValueError as e:
            logging.error("Invalid Input Value,Please Enter A Valid Integer Value.")
        
        # CALCULATE GRADE 
        grade=calculate_grade([maths,phy,chem,hindi,english])
        logging.info(f"Grade Calculated : {grade}")
        data={
            "maths":maths,
            "phy":phy,
            "chem":chem,
            "hindi":hindi,
            "english":english
        }
        # ADD THE MARKS INTO THE STUDENT DATA 
        try:
            # ADD THE MARKS 
            updatedData=simsCollection.find_one_and_update({"roll_number":roll_number},{"$set":{f"marks.{semester}":data,"grade":grade}},return_document=pymongo.ReturnDocument.AFTER)
            # SAVE THE LOG 
            logging.info(f"Marks Added Successfully,UpdatedData:{updatedData}")
            print("Marks Added Successfully!")
        except Exception as e:
            # SAVE THE LOG 
            logging.error(f"Error Occured In Adding Marks : {e}")
    # IF STUDENT NOT FOUND 
    else:
        # SAVE THE LOG 
        logging.warning("Invalid RollNumber")

# FIND CLASS STUDENT
def find_class_topper():
    logging.info("Find Class Topper Request Found")
    course=input("Enter Course : ").strip()
    semester=input("Enter Semester : ").strip()
    pipeline = [
        {"$match": {
            "course": course,
            f"marks.{semester}": {"$exists": True}
        }},
        {"$project": {
            "name": 1,
            "roll_number": 1,
            "total_marks": {
                "$sum": [
                    f"$marks.{semester}.maths",
                    f"$marks.{semester}.phy",
                    f"$marks.{semester}.chem",
                    f"$marks.{semester}.hindi",
                    f"$marks.{semester}.english"
                ]
            }
        }},
        {"$sort": {"total_marks": -1}},
        {"$limit": 1}
    ]

    result = list(simsCollection.aggregate(pipeline))
    if result:
        topper = result[0]
        print(f"\nTopper in {course}[Semester: {semester}] :\nName: {topper['name']}\nRoll Number: {topper['roll_number']}\nTotal Marks: {topper['total_marks']}")
    else:
        print("No data found for this course and semester.")


# DOENLOAD RESULT 
def download_result():
    logging.info("Download Result Request Fetched")
    # TAKE THE ROLL NUMBER AND SEMESTER OF THE STUDENT 
    roll_number = input("Enter Roll Number Of The Student : ").strip()
    semester = input("Enter Semester Of The Student : ").strip()

    try:
        # FETCH STUDENT DATA FROM MONGODB
        student = simsCollection.find_one({"roll_number": roll_number})
        if not student:
            logging.warning("Invalid Roll Number Provided For Download")
            print("Student not found!")
            return

        marks = student.get("marks", {}).get(semester)
        if not marks:
            logging.warning("Marks Not Found For Given Semester")
            print("No marks found for this semester!")
            return

        # PREPARE DATA FOR CSV
        data = {
            "Name": [student["name"]],
            "Roll Number": [student["roll_number"]],
            "Course": [student["course"]],
            "Semester": [semester],
            "Maths": [marks.get("maths", "N/A")],
            "Physics": [marks.get("phy", "N/A")],
            "Chemistry": [marks.get("chem", "N/A")],
            "Hindi": [marks.get("hindi", "N/A")],
            "English": [marks.get("english", "N/A")],
            "Grade": [student.get("grade", "N/A")]
        }

        df = pd.DataFrame(data)

        # CREATE DOWNLOAD DIRECTORY
        download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(download_path, exist_ok=True)

        # SAVE AS CSV FILE
        filename = f"{student['roll_number']}_Semester{semester}_Result.csv"
        file_path = os.path.join(download_path, filename)
        df.to_csv(file_path, index=False)

        logging.info(f"Result Downloaded Successfully At: {file_path}")
        print(f"Result downloaded successfully! Location: {file_path}")

    except Exception as e:
        logging.error(f"Error Occurred During Result Download: {e}")
        print("Something went wrong while downloading the result.")


# VISUALISE PERFORMANCE 
def visualise_performance():
    logging.info("Visualise Student Performance Request Fetched")
    roll_number=input("Enter Roll Number Of Student : ").strip()
    student = simsCollection.find_one({"roll_number": roll_number})
    if not student or "marks" not in student:
        print("No marks data found!")
        return
    # FETCH THE MARKS OF ALL SEMESTER OF STUDENT 
    marks = student["marks"]
    
    # TRANSPOSE THE DATA 
    df = pd.DataFrame(marks).T
    df.index.name = "semester"
    print(df)
    
    df.T.plot(kind='bar')
    # df.plot(kind='line', marker='o', figsize=(10,6))
    plt.title(f"Performance of {student['name']} across semesters")
    plt.ylabel("Marks")
    plt.xlabel("Semester")
    plt.grid(True)
    plt.legend(title="Subjects")
    plt.tight_layout()
    plt.show()

# GPA CALCULATOR 
def calculate_gpa():
    logging.info("Calculate Gpa Request Fetched")
    
    # FETCH THE ROLL NUMBER OF STUDENT 
    roll_number=input("Enter Roll Number : ")
    semester=input("Enter Semester : ")
    
    # FIND THE STUDENT ASSOCIATED WITH THE GIVEN ROLL NUMBER 
    student=simsCollection.find_one({"roll_number":roll_number})
    marks=student['marks']
    marks_dict=marks[semester]
    total_marks = sum(marks_dict.values())
    subjects = len(marks_dict)
    percentage = total_marks / (subjects * 100) * 100
    gpa = (percentage / 10) 
    gpa=round(gpa, 2)
    print(f"The GPA Of {student['name']} Of Semester:{semester} Is : {gpa}")




# ******************************* MESSAGE **************************************
flag=True
def message():
    global flag
    print("*****************************************   Enter An Option **********************************************")
    userInput=int(input("1.Add Student\n2.Delete Student\n3.Update Student\n4.Add Marks\n5.Find Class Topper\n6.Download Result\n7.Visualise Performance\n8.Find GPA\n9.Exit\n"))
    if userInput==1:
        add_student()
    elif userInput==2:
        delete_student()
    elif userInput==3:
        update_student()
    elif userInput==4:
        store_marks()
    elif userInput==5:
        find_class_topper()
    elif userInput==6:
        download_result()
    elif userInput==7:
        visualise_performance()
    elif userInput==8:
        calculate_gpa()
    elif userInput==9:
        flag=False
    else:
        print("Invalid Input!")
        
while flag:
    message()
        
        