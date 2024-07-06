import base64
from bson import ObjectId
from fastapi import FastAPI, HTTPException,UploadFile,File,Form,Cookie,Response,Depends
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from gridfs import GridFS
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.mount("/front", StaticFiles(directory="front"), name="front")


client = MongoClient('mongodb://localhost:27017/')
db = client['data']
fs = GridFS(db, collection="files")
reprint_document=GridFS(db, collection="reprint_document")
phd_certificate_document = GridFS(db, collection="phd_certificate_document")
pg_documents_document = GridFS(db, collection="pg_documents_document")
ug_documents_document = GridFS(db, collection="ug_documents_document")
diploma_documents_document = GridFS(db, collection="diploma_documents_document")
ssc_documents_document = GridFS(db, collection="ssc_documents_document")
pay_slip_document = GridFS(db, collection="pay_slip_document")
noc_undertaking_document = GridFS(db, collection="noc_undertaking_document")
experience_certificates_document = GridFS(db, collection="experience_certificates_document")
other_documents_document = GridFS(db, collection="other_documents_document")

gri=[reprint_document,phd_certificate_document,pg_documents_document,ug_documents_document,diploma_documents_document,ssc_documents_document,pay_slip_document,noc_undertaking_document,experience_certificates_document,other_documents_document]

collection = db['sample']
page1_collection=db['1stpage']
page2_collection=db['2ndpage']
page3_collection=db['3rdpage']
page4_collection=db['4thpage']
page5_collection=db['5thpage']
page6_collection=db['6thpage']
page7_collection=db['7thpage']

smtp_server = 'your_smtp_server_address'
smtp_port = 587  # Port for TLS encryption
sender_email = 'your_email@example.com'
password = 'your_email_password'



verification_code:str="123"
session :str =None

@app.get("/")
async def root():
    with open("front/login.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content,status_code=200)

@app.get("/user_signup/{a}/{b}/{c}/{d}")
async def root(a:str,b:str,c:str,d:str):
    check=collection.find_one({"username":c})
    if bool(check):
        
        return {"message":"username already exists","status":False}
    else:
        
        collection.insert_one({"username":c,"password":d,"firstname":a,"lastname":b})
        return {"message":"","status":True}
    
@app.get("/us")
async def root(a:str,b:str,c:str,d:str):
    collection.insert_one({"username":c,"password":d,"firstname":a,"lastname":b})
    

@app.get("/user_login/{a}/{b}")
async def root(a:str,b:str,response:Response):
    check=collection.find_one({"username":a,"password":b})
    global session
    session=a
    if check:
        
        return{"message":"","status":True}
    else:
        return {"message":"incorrect credentials","status":False}
    


@app.post("/1stpage")
async def root(
            middleName:str=Form(...) ,
            nationality:str=Form(...)  ,
            gender:str= Form(...),
            idProofFile:UploadFile=File(...),
            maritalStatus:str=Form(...),
            fathersName:str=Form(...),
            idProof:str=Form(...),
            address:str=Form(...),
            permanentAddress:str=Form(...),
            alternativeEmail:str=Form(...),
            mobileNumber:str=Form(...),
            alternativeNumber:str=Form(...)
            ):
        global session
        if session:
            if page1_collection.find_one({"username":session}):
                if idProofFile.content_type != "application/octet-stream":
                    fs.delete(page1_collection.find_one({"username":session})["file_id"])
                    file_id=fs.put(idProofFile.file,filename=session,content_type=idProofFile.content_type)
                    page1_collection.update_one({"status":True,"username":session},{"$set":{"mobileNumber":mobileNumber,"alternativeNumber":alternativeNumber,"alternativeEmail":alternativeEmail,"permanentAddress":permanentAddress,"address":address,"idProof":idProof,"fathersName":fathersName,"maritalStatus":maritalStatus,"middlename":middleName,"nationality":nationality,"gender":gender,"file_id":file_id}})
                else:
                    page1_collection.update_one({"status":True,"username":session},{"$set":{"mobileNumber":mobileNumber,"alternativeNumber":alternativeNumber,"alternativeEmail":alternativeEmail,"permanentAddress":permanentAddress,"address":address,"idProof":idProof,"fathersName":fathersName,"maritalStatus":maritalStatus,"middlename":middleName,"nationality":nationality,"gender":gender}})
            else:
                file_id=fs.put(idProofFile.file,filename=session,content_type=idProofFile.content_type)
                page1_collection.insert_one({"username":session,"middlename":middleName,"mobileNumber":mobileNumber,"alternativeNumber":alternativeNumber,"alternativeEmail":alternativeEmail,"permanentAddress":permanentAddress,"address":address,"idProof":idProof,"fathersName":fathersName,"maritalStatus":maritalStatus,"nationality":nationality,"gender":gender,"file_id":file_id})
        with open("front/2ndpage.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content,status_code=200)

            
@app.get("/file")
async def root():
    global session
    if page1_collection.find_one({"username":session}):
        file_id=page1_collection.find_one({"username":session})["file_id"]
        file_data = fs.get(ObjectId(file_id))

        # Encode file content as base64
        file_content = file_data.read()
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        # Determine file content type (e.g., image/jpeg)
        content_type = file_data.content_type

        # Return file data in HTTP response
        return {
            "status":True,
            "file_id": str(file_id),
            "content_type": content_type,
            "file_content": encoded_content
        } 
    else :
        return{"status":False}
    

@app.get("/file/{item}/{i}")
async def root(item:str ,i:int):
    global session
    if page7_collection.find_one({"username":session}):
        dic2=["reprint_document","phd_certificate_document","pg_documents_document","ug_documents_document","diploma_documents_document","ssc_documents_document","pay_slip_document","noc_undertaking_document","experience_certificates_document","other_documents_document"]
        global gri
        js={"status":True}
       
        temp1=item+"_file_id"
        temp2=page7_collection.find_one({"username":session})[temp1]
        info=gri[i].get((temp2))
        yu=info.read()
        content=base64.b64encode(yu).decode('utf-8')
        
        content_type=info.content_type
        js.update({

            
            "content_type_":content_type,
            "file_content_":content

        })
        print(js)
        return js
    else:
        return{"status":False}

@app.get("/logout")
async def root():
    global session
    session=""
    return({"status":"true"})

@app.get("/session1")
async def root():
    global session
    if session :       
        js={"status":True} 
        my_dict=page1_collection.find_one({"username":session})
        for key, value in my_dict.items():
            if not isinstance(value, ObjectId):
                js.update({key:value})
        return(js)
    else:
        return({"status":False})
    


@app.post("/2ndpage")
async def submit_education(
    phd_university: str = Form(...),
    phd_department: str = Form(...),
    phd_supervisor: str = Form(...),
    phd_joining_year: str = Form(...),
    phd_defence_date: str = Form(...),
    phd_award_date: str = Form(...),
    phd_thesis_title: str = Form(...),
    masters_degree: str = Form(...),
    masters_university: str = Form(...),
    masters_branch: str = Form(...),
    masters_joining_year: str = Form(...),
    masters_completion_year: str = Form(...),
    masters_duration: str = Form(...),
    masters_percentage: str = Form(...),
    masters_division: str = Form(...),
    bachelors_degree: str = Form(...),
    bachelors_university: str = Form(...),
    bachelors_branch: str = Form(...),
    bachelors_joining_year: str = Form(...),
    bachelors_completion_year: str = Form(...),
    bachelors_duration: str = Form(...),
    bachelors_percentage: str = Form(...),
    bachelors_division: str = Form(...),
    school_id_12 :str =Form(...),
    school_id_10 : str=Form(...),
    school_passing_year_12 : str =Form(...),
    school_passing_year_10 : str = Form(...),
    school_percentage_12:str=Form(...),
    school_percentage_10:str=Form(...),
    school_division_12:str=Form(...),
    school_division_10:str=Form(...),
    additional_degree: str =Form(...),
    additional_university: str  =Form(...),
    additional_branch: str =Form(...),
    additional_joining_year: str =Form(...),
    additional_completion_year: str =Form(...),
    additional_duration: str =Form(...),
    additional_percentage: str =Form(...),
    additional_division: str =Form(...),
    additional_degree2: str =Form(...),
    additional_university2: str  =Form(...),
    additional_branch2: str =Form(...),
    additional_joining_year2: str =Form(...),
    additional_completion_year2: str =Form(...),
    additional_duration2: str =Form(...),
    additional_percentage2: str =Form(...),
    additional_division2: str =Form(...),
    additional_degree3: str =Form(...),
    additional_university3: str  =Form(...),
    additional_branch3: str =Form(...),
    additional_joining_year3: str =Form(...),
    additional_completion_year3: str =Form(...),
    additional_duration3: str =Form(...),
    additional_percentage3: str =Form(...),
    additional_division3: str =Form(...)
    # Add similar Form parameters for Bachelors, School, and Additional qualifications
    
):
    global session
    # Process the received data as needed
    all_data = {
        "username":session,
        "phd": {
            "phd_university": phd_university,
            "phd_department": phd_department,
            "phd_supervisor": phd_supervisor,
            "phd_joining_year": phd_joining_year,
            "phd_defence_date": phd_defence_date,
            "phd_award_date": phd_award_date,
            "phd_thesis_title": phd_thesis_title,
        },
        "masters": {
            "masters_degree": masters_degree,
            "masters_university": masters_university,
            "masters_branch": masters_branch,
            "masters_joining_year": masters_joining_year,
            "masters_completion_year": masters_completion_year,
            "masters_duration": masters_duration,
            "masters_percentage": masters_percentage,
            "masters_division": masters_division,
        },
        "bachelors": {
            "bachelors_degree": bachelors_degree,
            "bachelors_university": bachelors_university,
            "bachelors_branch": bachelors_branch,
            "bachelors_joining_year": bachelors_joining_year,
            "bachelors_completion_year": bachelors_completion_year,
            "bachelors_duration": bachelors_duration,
            "bachelors_percentage": bachelors_percentage,
            "bachelors_division": bachelors_division,
        },
        "l12thHSCDiploma":{
            "school_id_12":school_id_12,
            "school_passing_year_12":school_passing_year_12,
            "school_percentage_12":school_percentage_12,
            "school_division_12":school_division_12,
        },
        "l10th":{
            "school_id_10":school_id_10,
            "school_passing_year_10":school_passing_year_10,
            "school_percentage_10":school_percentage_10,
            "school_division_10":school_division_10,
        },
        "additional_qualifications":{
            "additional_degree":additional_degree,
            "additional_university":additional_university,
            "additional_branch":additional_branch,
            "additional_joining_year":additional_joining_year,
            "additional_completion_year":additional_completion_year,
            "additional_duration":additional_duration,
            "additional_percentage":additional_percentage,
            "additional_division":additional_division,
            "additional_degree2":additional_degree2,
            "additional_university2":additional_university2,
            "additional_branch2":additional_branch2,
            "additional_joining_year2":additional_joining_year2,
            "additional_completion_year2":additional_completion_year2,
            "additional_duration2":additional_duration2,
            "additional_percentage2":additional_percentage2,
            "additional_division2":additional_division2,
            "additional_degree3":additional_degree3,
            "additional_university3":additional_university3,
            "additional_branch3":additional_branch3,
            "additional_joining_year3":additional_joining_year3,
            "additional_completion_year3":additional_completion_year3,
            "additional_duration3":additional_duration3,
            "additional_percentage3":additional_percentage3,
            "additional_division":additional_division,
        }
       
    }
    if session:
        if page2_collection.find({"username":session}):
            page2_collection.update_one({"username":session},{"$set":all_data})
        else:
            page2_collection.insert_one(all_data)
        with open("front/3rdpage.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content,status_code=200)
    else:
        return{"msg":False}



@app.get("/session2")
async def root():
    global session
    if session :       
        js={"status":True} 
        my_dict=page2_collection.find_one({"username":session})
        for key, value in my_dict.items():
            if not isinstance(value, ObjectId):
                js.update({key:value})
        return(js)
    else:
        return({"status":False})
    

@app.post("/3rdpage")
async def root(
    position_present_1: str = Form(...),
    organization_present_1: str = Form(...),
    status_present_1: str = Form(...),
    joining_date_present_1: str = Form(...),
    leaving_date_present_1: str = Form(...),
    duration_present_1: str = Form(...),
    position_exp_1: str = Form(...),
    organization_exp_1: str = Form(...),
    status_exp_1: str = Form(...),
    joining_date_exp_1: str = Form(...),
    leaving_date_exp_1: str = Form(...),
    duration_exp_1: str = Form(...),
    position_exp_2: str = Form(...),
    organization_exp_2: str = Form(...),
    status_exp_2: str = Form(...),
    joining_date_exp_2: str = Form(...),
    leaving_date_exp_2: str = Form(...),
    duration_exp_2: str = Form(...),
    position_exp_3: str = Form(...),
    organization_exp_3: str = Form(...),
    status_exp_3: str = Form(...),
    joining_date_exp_3: str = Form(...),
    leaving_date_exp_3: str = Form(...),
    duration_exp_3: str = Form(...),
    position_research_1: str = Form(...),
    organization_research_1: str = Form(...),
    status_research_1: str = Form(...),
    joining_date_research_1: str = Form(...),
    leaving_date_research_1: str = Form(...),
    duration_research_1: str = Form(...),
    position_research_2: str = Form(...),
    organization_research_2: str = Form(...),
    status_research_2: str = Form(...),
    joining_date_research_2: str = Form(...),
    leaving_date_research_2: str = Form(...),
    duration_research_2: str = Form(...),
    position_research_3: str = Form(...),
    organization_research_3: str = Form(...),
    status_research_3: str = Form(...),
    joining_date_research_3: str = Form(...),
    leaving_date_research_3: str = Form(...),
    duration_research_3: str = Form(...)
    ):
    global session
    all_data={
        "username":session,
        "present_employment":{
            "position_present_1":position_present_1,
            "organization_present_1":organization_present_1,
            "status_present_1":status_present_1,
            "joining_date_present_1":joining_date_present_1,
            "leaving_date_present_1":leaving_date_present_1,
            "duration_present_1":duration_present_1,
        },
        "employment_teaching_experince":{
            "position_exp_1":position_exp_1,
            "organization_exp_1":organization_exp_1,
            "status_exp_1":status_exp_1,
            "joining_date_exp_1":joining_date_exp_1,
            "leaving_date_exp_1":leaving_date_exp_1,
            "duration_exp_1":duration_exp_1,
            "position_exp_2":position_exp_2,
            "organization_exp_2":organization_exp_2,
            "status_exp_2":status_exp_2,
            "joining_date_exp_2":joining_date_exp_2,
            "leaving_date_exp_2":leaving_date_exp_2,
            "duration_exp_2":duration_exp_2,
            "position_exp_3":position_exp_3,
            "organization_exp_3":organization_exp_3,
            "status_exp_3":status_exp_3,
            "joining_date_exp_3":joining_date_exp_3,
            "leaving_date_exp_3":leaving_date_exp_3,
            "duration_exp_3":duration_exp_3
        },
        "research_experince":{
            "position_research_1":position_research_1,
            "organization_research_1":organization_research_1,
            "status_research_1":status_research_1,
            "joining_date_research_1":joining_date_research_1,
            "leaving_date_research_1":leaving_date_research_1,
            "duration_research_1":duration_research_1,
            "position_research_2":position_research_2,
            "organization_research_2":organization_research_2,
            "status_research_2":status_research_2,
            "joining_date_research_2":joining_date_research_2,
            "leaving_date_research_2":leaving_date_research_2,
            "duration_research_2":duration_research_2,
            "position_research_3":position_research_3,
            "organization_research_3":organization_research_3,
            "status_research_3":status_research_3,
            "joining_date_research_3":joining_date_research_3,
            "leaving_date_research_3":leaving_date_research_3,
            "duration_research_3":duration_research_3,
        }
    }
    if session:
        if page3_collection.find_one({"username":session}):
            page3_collection.update_one({"username":session},{"$set":all_data})
        else:
            page3_collection.insert_one(all_data)
        with open("front/4thpage.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content,status_code=200)


@app.get("/session3")
async def root():
    global session
    if session :       
        js={"status":True} 
        my_dict=page3_collection.find_one({"username":session})
        for key, value in my_dict.items():
            if not isinstance(value, ObjectId):
                js.update({key:value})
        return(js)
    else:
        return({"status":False})    


@app.post("/4thpage")
async def root(
    number_international_journal_papers : str = Form(...),
number_national_journal_papers : str = Form(...),
number_international_conference_papers : str = Form(...),
number_national_conference_papers : str = Form(...),
number_patents : str = Form(...),
number_books : str = Form(...),
number_book_chapters : str = Form(...),
author_1 : str = Form(...),
title_1 : str = Form(...),
journal_conference_1 : str = Form(...),
year_vol_page_1 : str = Form(...),
impact_factor_1 : str = Form(...),
doi_1 : str = Form(...),
status_1 : str = Form(...),
author_2 : str = Form(...),
title_2 : str = Form(...),
journal_conference_2 : str = Form(...),
year_vol_page_2 : str = Form(...),
impact_factor_2 : str = Form(...),
doi_2 : str = Form(...),
status_2 : str = Form(...),
author_3 : str = Form(...),
title_3 : str = Form(...),
journal_conference_3 : str = Form(...),
year_vol_page_3 : str = Form(...),
impact_factor_3 : str = Form(...),
doi_3 : str = Form(...),
status_3 : str = Form(...),
author_4 : str = Form(...),
title_4 : str = Form(...),
journal_conference_4 : str = Form(...),
year_vol_page_4 : str = Form(...),
impact_factor_4 : str = Form(...),
doi_4 : str = Form(...),
status_4 : str = Form(...),
author_5 : str = Form(...),
title_5 : str = Form(...),
journal_conference_5 : str = Form(...),
year_vol_page_5 : str = Form(...),
impact_factor_5 : str = Form(...),
doi_5 : str = Form(...),
status_5 : str = Form(...),
inventors_1 : str = Form(...),
title_patent_book_1 : str = Form(...),
country_1 : str = Form(...),
patent_number_1 : str = Form(...),
date_filing_1 : str = Form(...),
date_published_1 : str = Form(...),
status_patent_book_1 : str = Form(...),
inventors_2 : str = Form(...),
title_patent_book_2 : str = Form(...),
country_2 : str = Form(...),
patent_number_2 : str = Form(...),
date_filing_2 : str = Form(...),
date_published_2 : str = Form(...),
status_patent_book_2 : str = Form(...),
inventors_3 : str = Form(...),
title_patent_book_3 : str = Form(...),
country_3 : str = Form(...),
patent_number_3 : str = Form(...),
date_filing_3 : str = Form(...),
date_published_3 : str = Form(...),
status_patent_book_3 : str = Form(...),
inventors_4 : str = Form(...),
title_patent_book_4 : str = Form(...),
country_4 : str = Form(...),
patent_number_4 : str = Form(...),
date_filing_4 : str = Form(...),
date_published_4 : str = Form(...),
status_patent_book_4 : str = Form(...),
inventors_5 : str = Form(...),
title_patent_book_5 : str = Form(...),
country_5 : str = Form(...),
patent_number_5 : str = Form(...),
date_filing_5 : str = Form(...),
date_published_5 : str = Form(...),
status_patent_book_5 : str = Form(...),
google_scholar_link : str = Form(...),
):
    global session
    all_data={
        "username":session,
        "summary_publication":{
            "number_international_journal_papers": number_international_journal_papers,
"number_national_journal_papers": number_national_journal_papers,
"number_international_conference_papers": number_international_conference_papers,
"number_national_conference_papers": number_national_conference_papers,
"number_patents": number_patents,
"number_books": number_books,
"number_book_chapters": number_book_chapters,

        },
        "best_publication":{
            "author_1": author_1,
"title_1": title_1,
"journal_conference_1": journal_conference_1,
"year_vol_page_1": year_vol_page_1,
"impact_factor_1": impact_factor_1,
"doi_1": doi_1,
"status_1": status_1,
"author_2": author_2,
"title_2": title_2,
"journal_conference_2": journal_conference_2,
"year_vol_page_2": year_vol_page_2,
"impact_factor_2": impact_factor_2,
"doi_2": doi_2,
"status_2": status_2,
"author_3": author_3,
"title_3": title_3,
"journal_conference_3": journal_conference_3,
"year_vol_page_3": year_vol_page_3,
"impact_factor_3": impact_factor_3,
"doi_3": doi_3,
"status_3": status_3,
"author_4": author_4,
"title_4": title_4,
"journal_conference_4": journal_conference_4,
"year_vol_page_4": year_vol_page_4,
"impact_factor_4": impact_factor_4,
"doi_4": doi_4,
"status_4": status_4,
"author_5": author_5,
"title_5": title_5,
"journal_conference_5": journal_conference_5,
"year_vol_page_5": year_vol_page_5,
"impact_factor_5": impact_factor_5,
"doi_5": doi_5,
"status_5": status_5,

        },
        "patents":{
            "inventors_1": inventors_1,
"title_patent_book_1": title_patent_book_1,
"country_1": country_1,
"patent_number_1": patent_number_1,
"date_filing_1": date_filing_1,
"date_published_1": date_published_1,
"status_patent_book_1": status_patent_book_1,
"inventors_2": inventors_2,
"title_patent_book_2": title_patent_book_2,
"country_2": country_2,
"patent_number_2": patent_number_2,
"date_filing_2": date_filing_2,
"date_published_2": date_published_2,
"status_patent_book_2": status_patent_book_2,
"inventors_3": inventors_3,
"title_patent_book_3": title_patent_book_3,
"country_3": country_3,
"patent_number_3": patent_number_3,
"date_filing_3": date_filing_3,
"date_published_3": date_published_3,
"status_patent_book_3": status_patent_book_3,
"inventors_4": inventors_4,
"title_patent_book_4": title_patent_book_4,
"country_4": country_4,
"patent_number_4": patent_number_4,
"date_filing_4": date_filing_4,
"date_published_4": date_published_4,
"status_patent_book_4": status_patent_book_4,
"inventors_5": inventors_5,
"title_patent_book_5": title_patent_book_5,
"country_5": country_5,
"patent_number_5": patent_number_5,
    "date_filing_5": date_filing_5,
    "date_published_5": date_published_5,
    "status_patent_book_5": status_patent_book_5,

        },
        "scholar_link":{
            "google_scholar_link": google_scholar_link,
        }

    }
    if session:
        if page4_collection.find_one({"username":session}):
            page4_collection.update_one({"username":session},{"$set":all_data})
        else:
            page4_collection.insert_one(all_data)
        with open("front/5thpage.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content,status_code=200)
    
@app.get("/session4")
async def root():
    global session
    if session :       
        js={"status":True} 
        my_dict=page4_collection.find_one({"username":session})
        for key, value in my_dict.items():
            if not isinstance(value, ObjectId):
                js.update({key:value})
        return(js)
    else:
        return({"status":False}) 

@app.post("/5thpage")
async def root(
name_of_professional_society_1: str = Form(...),
membership_status_1: str = Form(...),
name_of_professional_society_2: str = Form(...),
membership_status_2: str = Form(...),
name_of_professional_society_3: str = Form(...),
membership_status_3: str = Form(...),
name_of_professional_society_4: str = Form(...),
membership_status_4: str = Form(...),
name_of_professional_society_5: str = Form(...),
membership_status_5: str = Form(...),
type_of_training_received_1: str = Form(...),
organisation_1: str = Form(...),
year_1: str = Form(...),
duration_1: str = Form(...),
type_of_training_received_2: str = Form(...),
organisation_2: str = Form(...),
year_2: str = Form(...),
duration_2: str = Form(...),
type_of_training_received_3: str = Form(...),
organisation_3: str = Form(...),
year_3: str = Form(...),
duration_3: str = Form(...),
type_of_training_received_4: str = Form(...),
organisation_4: str = Form(...),
year_4: str = Form(...),
duration_4: str = Form(...),
type_of_training_received_5: str = Form(...),
organisation_5: str = Form(...),
year_5: str = Form(...),
duration_5: str = Form(...),
name_of_award_1: str = Form(...),
awarded_by_1: str = Form(...),
award_year_1: str = Form(...),
name_of_award_2: str = Form(...),
awarded_by_2: str = Form(...),
award_year_2: str = Form(...),
name_of_award_3: str = Form(...),
awarded_by_3: str = Form(...),
award_year_3: str = Form(...),
sponsoring_agency_1: str = Form(...),
project_title_1: str = Form(...),
sanctioned_amount_1: str = Form(...),
project_period_1: str = Form(...),
project_role_1: str = Form(...),
project_status_1: str = Form(...),
sponsoring_agency_2: str = Form(...),
project_title_2: str = Form(...),
sanctioned_amount_2: str = Form(...),
project_period_2: str = Form(...),
project_role_2: str = Form(...),
project_status_2: str = Form(...),
sponsoring_agency_3: str = Form(...),
project_title_3: str = Form(...),
sanctioned_amount_3: str = Form(...),
project_period_3: str = Form(...),
project_role_3: str = Form(...),
project_status_3: str = Form(...),
sponsoring_agency_4: str = Form(...),
project_title_4: str = Form(...),
sanctioned_amount_4: str = Form(...),
project_period_4: str = Form(...),
project_role_4: str = Form(...),
project_status_4: str = Form(...),
sponsoring_agency_5: str = Form(...),
project_title_5: str = Form(...),
sanctioned_amount_5: str = Form(...),
project_period_5: str = Form(...),
project_role_5: str = Form(...),
project_status_5: str = Form(...),
consultancy_organization_1: str = Form(...),
consultancy_title_1: str = Form(...),
consultancy_grant_1: str = Form(...),
consultancy_period_1: str = Form(...),
consultancy_role_1: str = Form(...),
consultancy_status_1: str = Form(...),
consultancy_organization_2: str = Form(...),
consultancy_title_2: str = Form(...),
consultancy_grant_2: str = Form(...),
consultancy_period_2: str = Form(...),
consultancy_role_2: str = Form(...),
consultancy_status_2: str = Form(...),
consultancy_organization_3: str = Form(...),
consultancy_title_3: str = Form(...),
consultancy_grant_3: str = Form(...),
consultancy_period_3: str = Form(...),
consultancy_role_3: str = Form(...),
consultancy_status_3: str = Form(...),
consultancy_organization_4: str = Form(...),
consultancy_title_4: str = Form(...),
consultancy_grant_4: str = Form(...),
consultancy_period_4: str = Form(...),
consultancy_role_4: str = Form(...),
consultancy_status_4: str = Form(...),
consultancy_organization_5: str = Form(...),
consultancy_title_5: str = Form(...),
consultancy_grant_5: str = Form(...),
consultancy_period_5: str = Form(...),
consultancy_role_5: str = Form(...),
consultancy_status_5: str = Form(...),
):
    global session
    all_data={
        "username":session,
        
  "membership_of_professional_societies": {
    "name_of_professional_society_1": name_of_professional_society_1,
    "membership_status_1": membership_status_1,
    "name_of_professional_society_2": name_of_professional_society_2,
    "membership_status_2": membership_status_2,
    "name_of_professional_society_3": name_of_professional_society_3,
    "membership_status_3": membership_status_3,
    "name_of_professional_society_4": name_of_professional_society_4,
    "membership_status_4": membership_status_4,
    "name_of_professional_society_5": name_of_professional_society_5,
    "membership_status_5": membership_status_5
  },
  "professional_training": {
    "type_of_training_received_1": type_of_training_received_1,
    "organisation_1": organisation_1,
    "year_1": year_1,
    "duration_1": duration_1,
    "type_of_training_received_2": type_of_training_received_2,
    "organisation_2": organisation_2,
    "year_2": year_2,
    "duration_2": duration_2,
    "type_of_training_received_3": type_of_training_received_3,
    "organisation_3": organisation_3,
    "year_3": year_3,
    "duration_3": duration_3,
    "type_of_training_received_4": type_of_training_received_4,
    "organisation_4": organisation_4,
    "year_4": year_4,
    "duration_4": duration_4,
    "type_of_training_received_5": type_of_training_received_5,
    "organisation_5": organisation_5,
    "year_5": year_5,
    "duration_5": duration_5
  },
  "awards_and_recognition": {
    "name_of_award_1": name_of_award_1,
    "awarded_by_1": awarded_by_1,
    "award_year_1": award_year_1,
    "name_of_award_2": name_of_award_2,
    "awarded_by_2": awarded_by_2,
    "award_year_2": award_year_2,
    "name_of_award_3": name_of_award_3,
    "awarded_by_3": awarded_by_3,
    "award_year_3": award_year_3
  },
  "sponsored_projects": {
    "sponsoring_agency_1": sponsoring_agency_1,
    "project_title_1": project_title_1,
    "sanctioned_amount_1": sanctioned_amount_1,
    "project_period_1": project_period_1,
    "project_role_1": project_role_1,
    "project_status_1": project_status_1,
    "sponsoring_agency_2": sponsoring_agency_2,
    "project_title_2": project_title_2,
    "sanctioned_amount_2": sanctioned_amount_2,
    "project_period_2": project_period_2,
    "project_role_2": project_role_2,
    "project_status_2": project_status_2,
    "sponsoring_agency_3": sponsoring_agency_3,
    "project_title_3": project_title_3,
    "sanctioned_amount_3": sanctioned_amount_3,
    "project_period_3": project_period_3,
    "project_role_3": project_role_3,
    "project_status_3": project_status_3,
    "sponsoring_agency_4": sponsoring_agency_4,
    "project_title_4": project_title_4,
    "sanctioned_amount_4": sanctioned_amount_4,
    "project_period_4": project_period_4,
    "project_role_4": project_role_4,
    "project_status_4": project_status_4,
    "sponsoring_agency_5": sponsoring_agency_5,
    "project_title_5": project_title_5,
    "sanctioned_amount_5": sanctioned_amount_5,
    "project_period_5": project_period_5,
    "project_role_5": project_role_5,
    "project_status_5": project_status_5
  },
  "consultancy_details": {
    "consultancy_organization_1": consultancy_organization_1,
    "consultancy_title_1": consultancy_title_1,
    "consultancy_grant_1": consultancy_grant_1,
    "consultancy_period_1": consultancy_period_1,
    "consultancy_role_1": consultancy_role_1,
    "consultancy_status_1": consultancy_status_1,
    "consultancy_organization_2": consultancy_organization_2,
    "consultancy_title_2": consultancy_title_2,
    "consultancy_grant_2": consultancy_grant_2,
    "consultancy_period_2": consultancy_period_2,
    "consultancy_role_2": consultancy_role_2,
    "consultancy_status_2": consultancy_status_2,
    "consultancy_organization_3": consultancy_organization_3,
    "consultancy_title_3": consultancy_title_3,
    "consultancy_grant_3": consultancy_grant_3,
    "consultancy_period_3": consultancy_period_3,
    "consultancy_role_3": consultancy_role_3,
    "consultancy_status_3": consultancy_status_3,
    "consultancy_organization_4": consultancy_organization_4,
    "consultancy_title_4": consultancy_title_4,
    "consultancy_grant_4": consultancy_grant_4,
    "consultancy_period_4": consultancy_period_4,
    "consultancy_role_4": consultancy_role_4,
    "consultancy_status_4": consultancy_status_4,
    "consultancy_organization_5": consultancy_organization_5,
    "consultancy_title_5": consultancy_title_5,
    "consultancy_grant_5": consultancy_grant_5,
    "consultancy_period_5": consultancy_period_5,
    "consultancy_role_5": consultancy_role_5,
    "consultancy_status_5": consultancy_status_5
  
}
}
    if session:
        if page5_collection.find_one({"username":session}):
            page5_collection.update_one({"username":session},{"$set":all_data})
        else:
            page5_collection.insert_one(all_data)
        with open("front/6thpage.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content,status_code=200)
    
@app.get("/session5")
async def root():
    global session
    if session :       
        js={"status":True} 
        my_dict=page5_collection.find_one({"username":session})
        for key, value in my_dict.items():
            if not isinstance(value, ObjectId):
                js.update({key:value})
        return(js)
    else:
        return({"status":False}) 

@app.post("/6thpage")
async def root(
    phd_name_1: str = Form(...),
phd_title_1: str = Form(...),
phd_role_1: str = Form(...),
phd_status_1: str = Form(...),
phd_completion_1: str = Form(...),
phd_name_2: str = Form(...),
phd_title_2: str = Form(...),
phd_role_2: str = Form(...),
phd_status_2: str = Form(...),
phd_completion_2: str = Form(...),
phd_name_3: str = Form(...),
phd_title_3: str = Form(...),
phd_role_3: str = Form(...),
phd_status_3: str = Form(...),
phd_completion_3: str = Form(...),
    mtech_name_1: str = Form(...),
mtech_title_1: str = Form(...),
mtech_role_1: str = Form(...),
mtech_status_1: str = Form(...),
mtech_completion_1: str = Form(...),
mtech_name_2: str = Form(...),
mtech_title_2: str = Form(...),
mtech_role_2: str = Form(...),
mtech_status_2: str = Form(...),
mtech_completion_2: str = Form(...),
mtech_name_3: str = Form(...),
mtech_title_3: str = Form(...),
mtech_role_3: str = Form(...),
mtech_status_3: str = Form(...),
mtech_completion_3: str = Form(...),
    btech_name_1: str = Form(...),
btech_title_1: str = Form(...),
btech_role_1: str = Form(...),
btech_status_1: str = Form(...),
btech_completion_1: str = Form(...),
btech_name_2: str = Form(...),
btech_title_2: str = Form(...),
btech_role_2: str = Form(...),
btech_status_2: str = Form(...),
btech_completion_2: str = Form(...),
btech_name_3: str = Form(...),
btech_title_3: str = Form(...),
btech_role_3: str = Form(...),
btech_status_3: str = Form(...),
btech_completion_3: str = Form(...),
):
    global session
    all_data={
        "username":session,
        "phd":{
            "phd_name_1": phd_name_1,
"phd_title_1": phd_title_1,
"phd_role_1": phd_role_1,
"phd_status_1": phd_status_1,
"phd_completion_1": phd_completion_1,
"phd_name_2": phd_name_2,
"phd_title_2": phd_title_2,
"phd_role_2": phd_role_2,
"phd_status_2": phd_status_2,
"phd_completion_2": phd_completion_2,
"phd_name_3": phd_name_3,
"phd_title_3": phd_title_3,
"phd_role_3": phd_role_3,
"phd_status_3": phd_status_3,
"phd_completion_3": phd_completion_3,
        },
        "mtech":{
            "mtech_name_1": mtech_name_1,
"mtech_title_1": mtech_title_1,
"mtech_role_1": mtech_role_1,
"mtech_status_1": mtech_status_1,
"mtech_completion_1": mtech_completion_1,
"mtech_name_2": mtech_name_2,
"mtech_title_2": mtech_title_2,
"mtech_role_2": mtech_role_2,
"mtech_status_2": mtech_status_2,
"mtech_completion_2": mtech_completion_2,
"mtech_name_3": mtech_name_3,
"mtech_title_3": mtech_title_3,
"mtech_role_3": mtech_role_3,
"mtech_status_3": mtech_status_3,
"mtech_completion_3": mtech_completion_3,
        },
        "btech":{
            "btech_name_1": btech_name_1,
"btech_title_1": btech_title_1,
"btech_role_1": btech_role_1,
"btech_status_1": btech_status_1,
"btech_completion_1": btech_completion_1,
"btech_name_2": btech_name_2,
"btech_title_2": btech_title_2,
"btech_role_2": btech_role_2,
"btech_status_2": btech_status_2,
"btech_completion_2": btech_completion_2,
"btech_name_3": btech_name_3,
"btech_title_3": btech_title_3,
"btech_role_3": btech_role_3,
"btech_status_3": btech_status_3,
"btech_completion_3": btech_completion_3,
        }
    }

    if session:
        if page6_collection.find_one({"username":session}):
            page6_collection.update_one({"username":session},{"$set":all_data})
        else:
            page6_collection.insert_one(all_data)
        with open("front/7thpage.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content,status_code=200)
   

@app.get("/session6")
async def root():
    global session
    if session :       
        js={"status":True} 
        my_dict=page6_collection.find_one({"username":session})
        for key, value in my_dict.items():
            if not isinstance(value, ObjectId):
                js.update({key:value})
        return(js)
    else:
        return({"status":False}) 

@app.post("/7thpage")
async def root(
    reprint_document:UploadFile=File(...),
    phd_certificate_document:UploadFile=File(...),
    pg_documents_document:UploadFile=File(...),
    ug_documents_document:UploadFile=File(...),
    diploma_documents_document:UploadFile=File(...),
    ssc_documents_document:UploadFile=File(...),
    pay_slip_document:UploadFile=File(...),
    noc_undertaking_document:UploadFile=File(...),
    experience_certificates_document:UploadFile=File(...),
    other_documents_document:UploadFile=File(...),
    referee_name_1:str=Form(...),
    referee_position_1:str=Form(...),
    referee_association_1:str=Form(...),
    referee_institution_1:str=Form(...),
    referee_email_1:str=Form(...),
    referee_contact_1:str=Form(...),
    referee_name_2:str=Form(...),
    referee_position_2:str=Form(...),
    referee_association_2:str=Form(...),
    referee_institution_2:str=Form(...),
    referee_email_2:str=Form(...),
    referee_contact_2:str=Form(...),
    referee_name_3:str=Form(...),
    referee_position_3:str=Form(...),
    referee_association_3:str=Form(...),
    referee_institution_3:str=Form(...),
    referee_email_3:str=Form(...),
    referee_contact_3:str=Form(...),
):
    global session
    all_data={
        "referee":{
        "referee_name_1":referee_name_1,
        "referee_position_1":referee_position_1,
        "referee_association_1":referee_association_1,
        "referee_institution_1":referee_institution_1,
        "referee_email_1":referee_email_1,
        "referee_contact_1":referee_contact_1,
        "referee_name_2":referee_name_2,
        "referee_position_2":referee_position_2,
        "referee_association_2":referee_association_2,
        "referee_institution_2":referee_institution_2,
        "referee_email_2":referee_email_2,
        "referee_contact_2":referee_contact_2,
        "referee_name_3":referee_name_3,
        "referee_position_3":referee_position_3,
        "referee_association_3":referee_association_3,
        "referee_institution_3":referee_institution_3,
        "referee_email_3":referee_email_3,
        "referee_contact_3":referee_contact_3,
        }
    }

    dic=[reprint_document,phd_certificate_document,pg_documents_document,ug_documents_document,diploma_documents_document,ssc_documents_document,pay_slip_document,noc_undertaking_document,experience_certificates_document,other_documents_document]
    dic2=["reprint_document","phd_certificate_document","pg_documents_document","ug_documents_document","diploma_documents_document","ssc_documents_document","pay_slip_document","noc_undertaking_document","experience_certificates_document","other_documents_document"]

    global gri
    i=0
    if session:
        if page7_collection.find_one({"username":session}):
            for item in dic:
                
                if item.content_type != "application/octet-stream":
                    temp1=dic2[i]+"_file_id"
                    gri[i].delete(page7_collection.find_one({"username":session})[temp1])
                    temp2=gri[i].put(item.file,filename=session,content_type=item.content_type)
                    page7_collection.update_one({"username":session},{"$set":{temp1:temp2}})
                i=i+1
            page7_collection.update_one({"username":session},{"$set":all_data})
        else:
            for item in dic:
                temp1=dic2[i]+"_file_id"            
                temp2=gri[i].put(item.file,filename=session,content_type=item.content_type)
                all_data.update({"username":session,temp1:temp2})
                i=i+1
            page7_collection.insert_one(all_data)
        with open("front/8thpage.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content,status_code=200)


@app.get("/session7")
async def root():
    global session
    if session :       
        js={"status":True} 
        my_dict=page7_collection.find_one({"username":session})
        for key, value in my_dict.items():
            if not isinstance(value, ObjectId):
                js.update({key:value})
        return(js)
    else:
        return({"status":False}) 

@app.post("/forgot_password")
async def forgot_password(email: str):
    global session,verification_code
    # Generate a random 6-digit number
    verification_code = str(random.randint(100000, 999999))

    # Create a multipart message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = session
    message['Subject'] = 'Password Reset Verification Code'

    # Email body
    body = f'Your verification code for password reset is: {verification_code}'
    message.attach(MIMEText(body, 'plain'))

    try:
        # Establish a connection to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Start TLS encryption
            server.starttls()
            # Login to the email server
            server.login(sender_email, password)
            # Send the email
            server.sendmail(sender_email, session, message.as_string())
            return {"status": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/change_password/{code}/{new_password}")
async def root(code:str,new_password:str):
    global session
    global verification_code
    if session:
        if code == verification_code:
            collection.update_one({"username":session},{"$set":{"password":new_password}})
            return{"status":True}
    return{"status":False}