from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate ,logout
from django.contrib.auth import login as dj_login
from django.contrib.auth.models import User
from .models import Addmoney_info,UserProfile
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator, EmptyPage , PageNotAnInteger
from django.db.models import Sum
from django.http import JsonResponse
import datetime
from django.utils import timezone
import requests
import pandas as pd

from django.http import JsonResponse



from django.http import HttpResponse
import os
from django.conf import settings
from django.core.files.storage import default_storage
from openpyxl import Workbook

from expensewarninglib.warning import warning_notification

import os
import pandas as pd
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .models import Addmoney_info  
import boto3
from io import BytesIO




##################### WORKING ##############################



# def upload_to_s3(file_name, object_name=None):
#     bucket_name = "elasticbeanstalk-us-east-1-316190040777"

#     if object_name is None:
#         object_name = file_name.split("/")[-1]

#     s3_client = boto3.client('s3')
#     try:
#         s3_client.upload_file(file_name, bucket_name, object_name)
#         print(f"File '{file_name}' uploaded successfully to '{bucket_name}/{object_name}'")

#         presigned_url = s3_client.generate_presigned_url(
#             'get_object',
#             Params={'Bucket': bucket_name, 'Key': object_name},
#             ExpiresIn=86400  
#         )

#         print(f"Pre-signed URL: {presigned_url}")
#         return presigned_url
#     except FileNotFoundError:
#         print("Error: The file was not found.")
#     except Exception as e:
#         print(f"Error: {e}")
#     return None


# def send_email_via_sns(subject, message, file_url):
#     SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:316190040777:x23411520-SNS"
    
#     full_message = f"{message}\n\nDownload File: {file_url}"

#     try:
#         sns_client = boto3.client("sns", region_name="us-east-1")
#         response = sns_client.publish(
#             TopicArn=SNS_TOPIC_ARN,
#             Message=full_message,
#             Subject=subject
#         )
#         print(f"Email sent successfully! Message ID: {response['MessageId']}")
#         return True
#     except Exception as e:
#         print(f"Error sending email: {e}")
#         return False




def export_excel(request):
    try:
        data = Addmoney_info.objects.all().values()
        df = pd.DataFrame(data)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")
        output.seek(0)

        relative_path = "exports/data.xlsx"

        saved_path = default_storage.save(relative_path, ContentFile(output.read()))

        full_file_path = os.path.join(settings.MEDIA_ROOT, saved_path)
        # s3_file_url = upload_to_s3(full_file_path)

        # if s3_file_url:
        #     print("File successfully uploaded to S3")
        #     send_email_via_sns(
        #         subject="Your File is Ready for Download",
        #         message="Click the link below to download your file:",
        #         file_url=s3_file_url
        #     )
        # else:
        #     print("Error uploading file to S3")

        # Show success message and redirect
        messages.success(request, "Excel File Saved and Uploaded Successfully")
        return redirect("/tables")

    except Exception as e:
        print(f"Error in export_excel: {e}")
        messages.error(request, "Error exporting Excel file")
        return redirect("/tables")



def home(request):
    if request.session.has_key('is_logged'):
        return redirect('/index')
    return render(request,'home/login.html')
   # return HttpResponse('This is home')
def index(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        addmoney_info = Addmoney_info.objects.filter(user=user).order_by('-Date')
        paginator = Paginator(addmoney_info , 4)
        page_number = request.GET.get('page')
        page_obj = Paginator.get_page(paginator,page_number)
        context = {
            # 'add_info' : addmoney_info,
           'page_obj' : page_obj
        }
    #if request.session.has_key('is_logged'):
        return render(request,'home/index.html',context)
    return redirect('home')
    #return HttpResponse('This is blog')
def register(request):
    return render(request,'home/register.html')
    #return HttpResponse('This is blog')
def password(request):
    return render(request,'home/password.html')

def charts(request):
    return render(request,'home/charts.html')
def search(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        fromdate = request.GET['fromdate']
        todate = request.GET['todate']
        addmoney = Addmoney_info.objects.filter(user=user, Date__range=[fromdate,todate]).order_by('-Date')
        return render(request,'home/tables.html',{'addmoney':addmoney})
    return redirect('home')
def tables(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        addmoney = Addmoney_info.objects.filter(user=user).order_by('-Date')
        return render(request,'home/tables.html',{'addmoney':addmoney})
    return redirect('home')
def addmoney(request):
    return render(request,'home/addmoney.html')

def profile(request):
    if request.session.has_key('is_logged'):
        return render(request,'home/profile.html')
    return redirect('/home')

def profile_edit(request,id):
    if request.session.has_key('is_logged'):
        add = User.objects.get(id=id)
        # user_id = request.session["user_id"]
        # user1 = User.objects.get(id=user_id)
        return render(request,'home/profile_edit.html',{'add':add})
    return redirect("/home")

def profile_update(request,id):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user = User.objects.get(id=id)
            user.first_name = request.POST["fname"]
            user.last_name = request.POST["lname"]
            user.email = request.POST["email"]
            user.userprofile.Savings = request.POST["Savings"]
            user.userprofile.income = request.POST["income"]
            user.userprofile.profession = request.POST["profession"]
            user.userprofile.save()
            user.save()
            return redirect("/profile")
    return redirect("/home")   

# def handleSignup(request):
#     if request.method =='POST':
#             uname = request.POST["uname"]
#             fname=request.POST["fname"]
#             lname=request.POST["lname"]
#             email = request.POST["email"]
#             profession = request.POST['profession']
#             Savings = request.POST['Savings']
#             income = request.POST['income']
#             pass1 = request.POST["pass1"]
#             pass2 = request.POST["pass2"]
#             profile = UserProfile(Savings = Savings,profession=profession,income=income)
#             # check for errors in input
#             if request.method == 'POST':
#                 try:
#                     user_exists = User.objects.get(username=request.POST['uname'])
#                     messages.error(request," Username already taken, Try something else!!!")
#                     return redirect("/register")    
#                 except User.DoesNotExist:
#                     if len(uname)>15:
#                         messages.error(request," Username must be max 15 characters, Please try again")
#                         return redirect("/register")
            
#                     if not uname.isalnum():
#                         messages.error(request," Username should only contain letters and numbers, Please try again")
#                         return redirect("/register")
            
#                     if pass1 != pass2:
#                         messages.error(request," Password do not match, Please try again")
#                         return redirect("/register")
            
#             # create the user
#             user = User.objects.create_user(uname, email, pass1)
#             user.first_name=fname
#             user.last_name=lname
#             user.email = email
#             # profile = UserProfile.objects.all()

#             user.save()
#             # p1=profile.save(commit=False)
#             profile.user = user
#             profile.save()
#             messages.success(request," Your account has been successfully created")
#             return redirect("/")
#     else:
#         return HttpResponse('404 - NOT FOUND ')
#     return redirect('/login')





from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignupForm
from .models import UserProfile


#def handleSignup(request):
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignupForm
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignupForm
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)








# def handleSignup(request):
#     if request.method == "POST":
#         form = SignupForm(request.POST)
        
#         if form.is_valid():
#             try:
#                 # This will now create both User and UserProfile
#                 user = form.save()
                
#                 messages.success(request, "Your account has been successfully created.")
#                 return redirect("/login")
                
#             except Exception as e:
#                 logger.error(f"Error creating user: {str(e)}")
#                 # If there's an error, delete the user if it was created
#                 if User.objects.filter(username=form.cleaned_data.get('username')).exists():
#                     User.objects.filter(username=form.cleaned_data.get('username')).delete()
                
#                 messages.error(request, f"Error creating account: {str(e)}")
#                 return render(request, "register.html", {"form": form})
#         else:
#             # Print form errors to console for debugging
#             print("FORM ERRORS:")
#             for field, errors in form.errors.items():
#                 print(f"{field}: {errors}")
#             messages.error(request, "Please correct the errors below.")
#             return render(request, "register.html", {"form": form})
#     else:
#         form = SignupForm()
#         return render(request, "register.html", {"form": form})


def handleSignup(request):
    if request.method =='POST':
            # get the post parameters
            uname = request.POST["uname"]
            fname=request.POST["fname"]
            lname=request.POST["lname"]
            email = request.POST["email"]
            profession = request.POST['profession']
            Savings = request.POST['Savings']
            income = request.POST['income']
            pass1 = request.POST["pass1"]
            pass2 = request.POST["pass2"]
            profile = UserProfile(Savings = Savings,profession=profession,income=income)
            # check for errors in input
            if request.method == 'POST':
                try:
                    user_exists = User.objects.get(username=request.POST['uname'])
                    messages.error(request," Username already taken, Try something else!!!")
                    return redirect("/register")    
                except User.DoesNotExist:
                    if len(uname)>15:
                        messages.error(request," Username must be max 15 characters, Please try again")
                        return redirect("/register")
            
                    if not uname.isalnum():
                        messages.error(request," Username should only contain letters and numbers, Please try again")
                        return redirect("/register")
            
                    if pass1 != pass2:
                        messages.error(request," Password do not match, Please try again")
                        return redirect("/register")
            
            # create the user
            user = User.objects.create_user(uname, email, pass1)
            user.first_name=fname
            user.last_name=lname
            user.email = email
            # profile = UserProfile.objects.all()

            user.save()
            # p1=profile.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request," Your account has been successfully created")
            return redirect("/")
    else:
        return HttpResponse('404 - NOT FOUND ')
    return redirect('/login')




def handlelogin(request):
    if request.method =='POST':
        # get the post parameters
        loginuname = request.POST["loginuname"]
        loginpassword1=request.POST["loginpassword1"]
        user = authenticate(username=loginuname, password=loginpassword1)
        if user is not None:
            dj_login(request, user)
            request.session['is_logged'] = True
            user = request.user.id 
            request.session["user_id"] = user
            messages.success(request, " Successfully logged in")
            return redirect('/index')
        else:
            messages.error(request," Invalid Credentials, Please try again")  
            return redirect("/")  
    return HttpResponse('404-not found')
def handleLogout(request):
        del request.session['is_logged']
        del request.session["user_id"] 
        logout(request)
        messages.success(request, " Successfully logged out")
        return redirect('home')

#add money form
def addmoney_submission(request):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user_id = request.session["user_id"]
            user1 = User.objects.get(id=user_id)
            addmoney_info1 = Addmoney_info.objects.filter(user=user1).order_by('-Date')
            add_money = request.POST["add_money"]
            quantity = request.POST["quantity"]
            Date = request.POST["Date"]
            Category = request.POST["Category"]
            add = Addmoney_info(user = user1,add_money=add_money,quantity=quantity,Date = Date,Category= Category)
            add.save()
            paginator = Paginator(addmoney_info1, 4)
            page_number = request.GET.get('page')
            page_obj = Paginator.get_page(paginator,page_number)
            context = {
                'page_obj' : page_obj
                }
            return render(request,'home/index.html',context)
    return redirect('/index')

def addmoney_update(request,id):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            add  = Addmoney_info.objects.get(id=id)
            add .add_money = request.POST["add_money"]
            add.quantity = request.POST["quantity"]
            add.Date = request.POST["Date"]
            add.Category = request.POST["Category"]
            add .save()
            return redirect("/index")
    return redirect("/home")        

def expense_edit(request,id):
    if request.session.has_key('is_logged'):
        addmoney_info = Addmoney_info.objects.get(id=id)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        return render(request,'home/expense_edit.html',{'addmoney_info':addmoney_info})
    return redirect("/home")  

def expense_delete(request,id):
    if request.session.has_key('is_logged'):
        addmoney_info = Addmoney_info.objects.get(id=id)
        addmoney_info.delete()
        return redirect("/index")
    return redirect("/home")  

def expense_month(request):
    todays_date = datetime.date.today()
    one_month_ago = todays_date-datetime.timedelta(days=30)
    user_id = request.session["user_id"]
    user1 = User.objects.get(id=user_id)
    addmoney = Addmoney_info.objects.filter(user = user1,Date__gte=one_month_ago,Date__lte=todays_date)
    finalrep ={}

    def get_Category(addmoney_info):
        # if addmoney_info.add_money=="Expense":
        return addmoney_info.Category    
    Category_list = list(set(map(get_Category,addmoney)))

    def get_expense_category_amount(Category,add_money):
        quantity = 0 
        filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
        for item in filtered_by_category:
            quantity+=item.quantity
        return quantity

    for x in addmoney:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y,"Expense")

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats(request):
    if request.session.has_key('is_logged') :
        todays_date = datetime.date.today()
        one_month_ago = todays_date-datetime.timedelta(days=30)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney_info = Addmoney_info.objects.filter(user = user1,Date__gte=one_month_ago,Date__lte=todays_date)
        sum = 0 
        for i in addmoney_info:
            if i.add_money == 'Expense':
                sum=sum+i.quantity
        addmoney_info.sum = sum
        sum1 = 0 
        for i in addmoney_info:
            if i.add_money == 'Income':
                sum1 =sum1+i.quantity
        addmoney_info.sum1 = sum1
        x= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
        y= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
        if x<0:
            message = warning_notification()
            messages.warning(request,message)
            x = 0
        if x>0:
            y = 0
        addmoney_info.x = abs(x)
        addmoney_info.y = abs(y)
        return render(request,'home/stats.html',{'addmoney':addmoney_info})

def expense_week(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date-datetime.timedelta(days=7)
    user_id = request.session["user_id"]
    user1 = User.objects.get(id=user_id)
    addmoney = Addmoney_info.objects.filter(user = user1,Date__gte=one_week_ago,Date__lte=todays_date)
    finalrep ={}

    def get_Category(addmoney_info):
        return addmoney_info.Category
    Category_list = list(set(map(get_Category,addmoney)))


    def get_expense_category_amount(Category,add_money):
        quantity = 0 
        filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
        for item in filtered_by_category:
            quantity+=item.quantity
        return quantity

    for x in addmoney:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y,"Expense")

    return JsonResponse({'expense_category_data': finalrep}, safe=False)






def convert_to_usd(amount_in_inr):
    #API_URL = "https://hcu8ibrw8k.execute-api.eu-central-1.amazonaws.com/stage1/currency"
    API_URL = "https://t76k792r8a.execute-api.us-east-1.amazonaws.com/cur_convert"

    payload = {
        "amount": amount_in_inr,
        "from_currency": "INR",
        "to_currency": "USD"
    }
    try:
        response = requests.get(API_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get('converted_amount', 0)
        else:
            return 0
    except Exception as e:
        print(f"Error while converting to USD: {str(e)}")
        return 0

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Addmoney_info, UserProfile
import datetime


def weekly(request):

    if not request.session.has_key('is_logged'):
        return redirect('handlelogin')   # redirect to your login page

    user_id = request.session["user_id"]
    user1 = User.objects.get(id=user_id)

    profile, created = UserProfile.objects.get_or_create(user=user1)

    todays_date = datetime.date.today()
    one_week_ago = todays_date - datetime.timedelta(days=7)

    addmoney_info = Addmoney_info.objects.filter(
        user=user1,
        Date__gte=one_week_ago,
        Date__lte=todays_date
    )

    total_expense = sum(i.quantity for i in addmoney_info if i.add_money == 'Expense')
    total_income  = sum(i.quantity for i in addmoney_info if i.add_money == 'Income')

    addmoney_info.sum = total_expense
    addmoney_info.sum1 = total_income

    x = profile.Savings + total_income - total_expense
    y = profile.Savings + total_income - total_expense

    if x < 0:
        message = warning_notification()
        messages.warning(request, message)
        x = 0
    if x > 0:
        y = 0

    addmoney_info.x = abs(x)
    addmoney_info.y = abs(y)


    expense_in_usd = convert_to_usd(total_expense)
    savings_in_usd = convert_to_usd(addmoney_info.x)


    return render(request, 'home/weekly.html', {
        'addmoney_info': addmoney_info,
        'expense_in_usd': expense_in_usd,
        'savings_in_usd': savings_in_usd
    })



def check(request):
    if request.method == 'POST':
        user_exists = User.objects.filter(email=request.POST['email'])
        messages.error(request,"Email not registered, TRY AGAIN!!!")
        return redirect("/reset_password")

def info_year(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date-datetime.timedelta(days=30*12)
    user_id = request.session["user_id"]
    user1 = User.objects.get(id=user_id)
    addmoney = Addmoney_info.objects.filter(user = user1,Date__gte=one_week_ago,Date__lte=todays_date)
    finalrep ={}

    def get_Category(addmoney_info):
        return addmoney_info.Category
    Category_list = list(set(map(get_Category,addmoney)))


    def get_expense_category_amount(Category,add_money):
        quantity = 0 
        filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
        for item in filtered_by_category:
            quantity+=item.quantity
        return quantity

    for x in addmoney:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y,"Expense")

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def info(request):
    return render(request,'home/info.html')
     