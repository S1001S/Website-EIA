from typing import Counter
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import PoliceDetail, Criminal, Missing, Report, ReportUpdate, CriminalUpdate
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate,login,logout
import json
import os
import cv2
import face_recognition

file_urls=[]

def index(request):
    return render(request,'login/index.html')

def police_signup(request):
    if request.method=="POST":
        username=request.POST.get('policeusername','')
        firstname=request.POST.get('firstname','')
        lastname=request.POST.get('lastname','')
        email=request.POST.get('email','')
        password1=request.POST.get('password1','')
        password2=request.POST.get('password2','')
        picture=request.FILES['photo']
        if password1==password2:
                    if User.objects.filter(username=username).first():
                        messages.error(request,"Already exists")
                        return redirect('Login Page')
                    else:
                        policedetails=PoliceDetail(username=username,firstname=firstname,lastname=lastname,email=email,picture=picture)
                        policedetails.save()
                        policeuser=User.objects.create_user(username,email,password1)
                        policeuser.first_name=firstname
                        policeuser.last_name=lastname
                        policeuser.save()
                        user=Group.objects.get_or_create(name='Police')
                        policeuser.groups.add(user[0])
                        messages.success(request,"Your account has been successfully created")
                        return redirect("Login Page")
        else:
            messages.error(request,"Invalid Passwords")
            return redirect('Login Page')
    else:
        return redirect('Login Page')

def detect():
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    police=PoliceDetail.objects.all()
    known_face_names=[]
    known_face_encodings=[]
    for i in range(0,len(police)):
        imgtest=face_recognition.load_image_file(police[i].picture)
        encodetest=face_recognition.face_encodings(imgtest)[0]
        known_face_encodings.append(encodetest)
        known_face_names.append(police[i].username)
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    names=[]
    while True:
        ret, frame = video_capture.read()
        rgb_small_frame = frame[:, :, ::-1]
        if process_this_frame:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            name="Unknown"
            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    if name not in names:
                        names.append(name)
                face_names.append(name)
        process_this_frame = not process_this_frame
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        cv2.imshow('Video', frame)
        if cv2.waitKey(25)==13:
            break
    video_capture.release()
    cv2.destroyAllWindows()
    return(names)

def police_login(request):
    if request.method=="POST":
        name=detect()
        if len(name)!=0:
            username=name[0]
            password=request.POST.get('password','')
            user=authenticate(username=username,password=password)
            if user is not None and user.groups.filter(name='Police'):
                login(request,user)
                messages.success(request,'You are currently logged in.')
                return redirect('Police Login')
            else:
                messages.error(request,"Invalid Login Details. Please try again")
                return redirect('Login Page')
        else:
                messages.error(request,"Face not found. Please try again")
                return redirect('Login Page')
    else:
        return render(request,'login/police_login.html')

def citizen_register(request):
    if request.method=="POST":
        citizenusername=request.POST.get('citizenusername','')
        citizenfirstname=request.POST.get('citizenfirstname','')
        citizenlastname=request.POST.get('citizenlastname','')
        citizenemail=request.POST.get('citizenemail','')
        citizenpassword1=request.POST.get('citizenpassword1','')
        citizenpassword2=request.POST.get('citizenpassword2','')
        if citizenpassword1==citizenpassword2:
                    if User.objects.filter(username=citizenusername).first():
                        messages.error(request,"This username already exists")
                        return redirect('Login Page')
                    else:
                        citizenuser=User.objects.create_user(citizenusername,citizenemail,citizenpassword1)
                        citizenuser.first_name=citizenfirstname
                        citizenuser.last_name=citizenlastname
                        citizenuser.save()
                        user=Group.objects.get_or_create(name='Citizen')
                        citizenuser.groups.add(user[0])
                        messages.success(request,"Your account has been successfully created")
                        return redirect("Login Page")
        else:
            messages.error(request,"Invalid Passwords")
            return redirect('Login Page')
    else:
        return redirect('Login Page')


def citizen_login(request):
    if request.method=="POST":
        username=request.POST.get('cusername','')
        password=request.POST.get('citizenpassword','')
        user=authenticate(username=username,password=password)
        if user is not None and user.groups.filter(name='Citizen'):
            login(request,user)
            messages.success(request,'You are currently logged in.')
            return redirect('Citizen Login')
        else:
            messages.error(request,"Invalid Login Details. Please try again")
            return redirect('Login Page')
    else:
        return render(request,'login/citizen_login.html')

def add_criminals(request):
    if request.method=="POST":
        firstname=request.POST.get('firstname','')
        lastname=request.POST.get('lastname','')
        criminalid=request.POST.get('criminalid','')
        age=request.POST.get('age','')
        gender=request.POST.get('gender','')
        residence=request.POST.get('residence','')
        crime=request.POST.get('crime','')
        location=request.POST.get('location','')
        lat=request.POST.get('lat','')
        lng=request.POST.get('lng','')
        time=request.POST.get('time','')
        picture=request.FILES['picture']
        criminal=Criminal(firstname=firstname,lastname=lastname, criminalid=criminalid, age=age, gender=gender, residence=residence, crime=crime, picture=picture)
        criminal.save()
        update=CriminalUpdate(criminalid=criminal.criminalid,update_crime=crime,update_locations=location,lat=lat,lng=lng,time=time)
        update.save()
        messages.success(request,"Criminal Succesfully Added to the Database.")
        return redirect('Add Criminals')
    return render(request,'login/add_criminals.html')

def detect_criminal(request):
    if request.method=="POST":
        picture=request.FILES['picture']
        fss=FileSystemStorage()
        file=fss.save(picture.name,picture)
        file_url=fss.url(file)
        file_urls.append(file_url)
        detectimg=face_recognition.load_image_file(picture)
        detectimg=cv2.cvtColor(detectimg,cv2.COLOR_BGR2RGB)
        encodeorig=face_recognition.face_encodings(detectimg)[0]
        criminal=Criminal.objects.all()
        flag=0
        for i in range(0,len(criminal)):
            imgtest=face_recognition.load_image_file(criminal[i].picture)
            imgtest=cv2.cvtColor(imgtest,cv2.COLOR_BGR2RGB)
            encodetest=face_recognition.face_encodings(imgtest)[0]
            results=face_recognition.compare_faces([encodeorig],encodetest)
            if True in results:
                messages.success(request,"This Criminal exitsts in the database")
                flag=1
                params={'matched':criminal[i], 'picture_url':file_url,'check':flag}
                return render(request,'login/detected_criminal.html',params)
        messages.error(request,"Not Found")
        params={'picture_url':file_url,'check':flag}
        return render(request, 'login/detected_criminal.html', params)
    return render(request,'login/detect_criminal.html')

def video_detect(file_url):
    cap= cv2.VideoCapture(os.getcwd()+file_url)
    criminal=Criminal.objects.all()
    known_face_id=[]
    known_face_encodings=[]
    for i in range(0,len(criminal)):
        imgtest=face_recognition.load_image_file(criminal[i].picture)
        encodetest=face_recognition.face_encodings(imgtest)[0]
        known_face_encodings.append(encodetest)
        known_face_id.append(criminal[i].criminalid)
    face_locations = []
    face_encodings = []
    face_ids = []
    process_this_frame = True
    ids=[]
    while True:
        ret, frame = cap.read()
        if ret:
            rgb_frame = frame[:, :, ::-1]
            if process_this_frame:
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                face_ids = []
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    id="Unknown"
                    if True in matches:
                        first_match_index = matches.index(True)
                        id = known_face_id[first_match_index]
                        if id not in ids:
                            ids.append(id)
                    face_ids.append(id)
            process_this_frame = not process_this_frame
            for (top, right, bottom, left), id in zip(face_locations, face_ids):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, id, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            cv2.imshow('Video', frame)
            if cv2.waitKey(25)==13:
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()
    return ids

def detect_criminal_video(request):
    if request.method=="POST":
        video=request.FILES['video']
        fss=FileSystemStorage()
        file=fss.save(video.name,video)
        file_url=fss.url(file)
        file_urls.append(file_url)
        check=video_detect(file_url)
        if len(check)!=0:
            criminals=[]
            for i in check:
                criminal=Criminal.objects.filter(criminalid=i)
                criminals.append(criminal[0])
            messages.success(request,"Match found in database")
            params={'criminal':criminals}
            return render(request,'login/detected_criminal_video.html',params)
        else:
            messages.error(request,"No Criminals Found in database from the Given Video")
            return render(request,'login/detect_criminal.html')
    return render(request,'login/detect_criminal.html')



def missing_detect(request):
    if request.method=="POST":
        name=request.POST.get('name','')
        mobile=request.POST.get('mobile','')
        email=request.POST.get('email','')
        picture=request.FILES['picture']
        detectimg=face_recognition.load_image_file(picture)
        detectimg=cv2.cvtColor(detectimg,cv2.COLOR_BGR2RGB)
        encodeorig=face_recognition.face_encodings(detectimg)[0]
        missing=Missing.objects.filter(foundby="")
        for i in range(0,len(missing)):
            imgtest=face_recognition.load_image_file(missing[i].picture)
            imgtest=cv2.cvtColor(imgtest,cv2.COLOR_BGR2RGB)
            encodetest=face_recognition.face_encodings(imgtest)[0]
            results=face_recognition.compare_faces([encodeorig],encodetest)
            if True in results:
                messages.success(request,"Match Found! A mail has been sent to our agency. Thanks for helping us.")
                subject=missing[i].name+" Found"
                message=missing[i].name+ ", age "+ missing[i].age+ ", has been found by "+ name +", mobile number: " +mobile+", using email-id: "+email
                missing[i].foundpicture=picture
                missing[i].foundby=name
                missing[i].save()
                send_mail(
                    subject,
                    message,
                    email,
                    ['ssdjng92@gmail.com'],
                    fail_silently=False            
                )
                return render(request,'login/missing_detect.html')
        messages.error(request," Match Not Found!")
        return render(request, 'login/missing_detect.html')
    return render(request,'login/missing_detect.html')

def file_report(request):
    if request.method=="POST":
        name=request.POST.get('name','')
        mobile=request.POST.get('mobile','')
        aadhar=request.POST.get('aadhar','')
        gender=request.POST.get('gender','')
        residence=request.POST.get('residence','')
        description=request.POST.get('description','')
        picture1=request.FILES.get('picture1', False)
        picture2=request.FILES.get('picture2', False)
        picture3=request.FILES.get('picture3', False)
        video=request.FILES.get('video', False)
        report=Report(name=name, mobile=mobile, aadhar=aadhar, gender=gender, residence=residence, description=description, picture1=picture1, picture2=picture2, picture3=picture3, video=video)
        report.save()
        update=ReportUpdate(report_id=report.report_id, update_desc="Report Filed at our Investigative Agency.")
        update.save()
        thank=True
        id=report.report_id
        messages.success(request,"Report Filed at our Investigative Agency sucessfully.")
        return render(request,'login/file_report.html',{'thank':thank, 'id':id})
    report=Report.objects.filter(aadhar=request.user.username)
    params={'reports':report}
    return render(request,'login/file_report.html',params)

def update_report(request,pr_id):
    if request.method=="POST":
        update_desc=request.POST.get('update','')
        update=ReportUpdate(report_id=pr_id, update_desc=update_desc)
        update.save()
        messages.success(request,"Report Updated Successfully")
        result=Report.objects.filter(report_id=pr_id)
        params={'result':result[0]}
        return render(request,'login/update_report.html',params)
    result=Report.objects.filter(report_id=pr_id)
    params={'result':result[0]}
    return render(request,'login/update_report.html',params)

def update_criminal(request,pr_id):
    if request.method=="POST":
        update_crime=request.POST.get('updatecrime','')
        update_locations=request.POST.get('updatelocations','')
        lat=request.POST.get('lat','')
        lng=request.POST.get('lng','')
        timespot=request.POST.get('timespot','')
        update=CriminalUpdate(criminalid=pr_id, update_crime=update_crime, update_locations=update_locations, lat=lat,lng=lng, time=timespot)
        update.save()
        messages.success(request,"Report Updated Successfully")
        result=Criminal.objects.filter(criminalid=pr_id)
        params={'result':result[0]}
        return render(request,'login/update_criminal.html',params)
    result=Criminal.objects.filter(criminalid=pr_id)
    params={'result':result[0]}
    return render(request,'login/update_criminal.html',params)

def allreports(request):
    report=Report.objects.all()
    params={'report':report}
    return render(request,'login/allreports.html',params)

def allcriminals(request):
    criminal=Criminal.objects.all()
    loc=set()
    l=[]
    location=[]
    times=[]
    c=[]
    spottime=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    ttimes=[]
    for k in range(0,len(criminal)):
        update=CriminalUpdate.objects.filter(criminalid=criminal[k].criminalid)
        for i in range(0,len(update)):
            if update[i].update_locations!="":
                t=(update[i].time).hour
                loc.add(update[i].update_locations)
                l.append(update[i].update_locations)
                c.append(t)
    d=Counter(l)
    for i in loc:
        location.append(i)
        times.append(d[i])
    for i in spottime:
        ttimes.append(c.count(i))
    params={'criminal':criminal, 'location':location,'times':times,'spottime':spottime,'ttimes':ttimes}
    return render(request,'login/allcriminals.html',params)

def allmissing(request):
    missing=Missing.objects.all()
    params={'missing':missing}
    return render(request,'login/allmissing.html',params)

def criminalView(request, pr_id):
    result=Criminal.objects.filter(criminalid=pr_id)
    update=CriminalUpdate.objects.filter(criminalid=pr_id)
    loc=set()
    l=[]
    location=[]
    times=[]
    c=[]
    spottime=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    ttimes=[]
    for i in range(0,len(update)):
        if update[i].update_locations!="":
            t=(update[i].time).hour
            loc.add(update[i].update_locations)
            l.append(update[i].update_locations)
            c.append(t)
    d=Counter(l)
    for i in loc:
        location.append(i)
        times.append(d[i])
    for i in spottime:
        ttimes.append(c.count(i))
    params={'result':result[0], 'update':update,'location':location,'times':times,'spottime':spottime,'ttimes':ttimes}
    return render(request, 'login/search_criminal.html',params)

def reportView(request, pr_id):
    result=Report.objects.filter(report_id=pr_id)
    update=ReportUpdate.objects.filter(report_id=pr_id)
    params={'result':result[0], 'update':update}
    group=Group.objects.filter(user=request.user)
    if str(group[0])=="Police":
        return render(request, 'login/search_report.html',params)
    else:
        return render(request, 'login/citizen_report.html',params)

def missingView(request, pr_id):
    result=Missing.objects.filter(id=pr_id)
    params={'result':result[0]}
    return render(request, 'login/search_missing.html',params)

def add_missing(request):
    if request.method=="POST":
        name=request.POST.get('name','')
        age=request.POST.get('age','')
        gender=request.POST.get('gender','')
        contactperson=request.POST.get('contactperson','')
        contactnumber=request.POST.get('contactnumber','')
        picture=request.FILES['picture']
        missing=Missing(name=name, age=age, gender=gender, contactperson=contactperson, contactnumber=contactnumber, picture=picture)
        missing.save()
        messages.success(request,"Missing Case successfully added to the database.")
        return render(request,'login/add_missing.html')
    return render(request, 'login/add_missing.html')

def track_status(request):
    if request.method=="POST":
        report_id=request.POST.get('report_id','')
        aadhar=request.POST.get('aadhar','')
        try:
            report=Report.objects.filter(report_id=report_id, aadhar=aadhar)
            if len(report)!=0:
                update=ReportUpdate.objects.filter(report_id=report_id)
                updates=[]
                for i in update:
                    updates.append({'text':i.update_desc, 'time':i.timestamp})
                    response=json.dumps({"status":"success", "updates":updates}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')
    return render(request,'login/track_status.html')

def map_view(request,pr_id):
    update=CriminalUpdate.objects.filter(update_id=pr_id)
    params={'result':update[0]}
    return render(request,'login/map_view.html',params)

def handlelogout(request):
    for file in file_urls:
        os.remove(os.getcwd()+file)
    file_urls.clear()
    logout(request)
    messages.success(request,'Logged Out Successfully')
    return redirect('/')