from django.http import JsonResponse
from django.shortcuts import render, redirect,HttpResponse
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from firestoreconfig import db,bucket
import magic
import os
from dotenv import load_dotenv
import razorpay
load_dotenv()
import json

RAZORPAY_API_KEY = os.getenv('RAZORPAY_API_KEY')
RAZORPAY_API_SECRET = os.getenv('RAZORPAY_API_SECRET')
client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))


def home(request):
    return render(request,'main/index.html')

def header(request):
    return render(request,'main/header.html')

@csrf_protect
def create_cv(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact_info = request.POST.get('contact_info')
        email_web = request.POST.get('email_web')
        website = request.POST.get('website')
        profile_photo = request.FILES.get('profile_photo')
        phone = request.POST.get('phone')
        languages_known = request.POST.get('languages_known').split(',')
        skills = request.POST.get('skills').split(',')

        experiences = []
        for key in request.POST:
            if key.startswith('experiences['):
                index = key.split('[')[1].split(']')[0]
                if index.isdigit():
                    index = int(index)
                    while len(experiences) <= index:
                        experiences.append({})
                    experiences[index][key.split('][')[1].split(']')[0]] = request.POST[key]

        educations = []
        for key in request.POST:
            if key.startswith('educations['):
                index = key.split('[')[1].split(']')[0]
                if index.isdigit():
                    index = int(index)
                    while len(educations) <= index:
                        educations.append({})
                    educations[index][key.split('][')[1].split(']')[0]] = request.POST[key]

        resume_ref = db.collection('resumes').document()
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(profile_photo.read())
        profile_photo.seek(0)

        blob = bucket.blob(f'profile_photos/{profile_photo.name}')
        blob.upload_from_file(profile_photo, content_type=mime_type)
        # blob.make_public()

        resume_data = {
            'first_name': first_name.upper(),
            'last_name': last_name.upper(),
            'contact_info': contact_info,
            'email_web': email_web,
            'website': website,
            'profile_photo': blob.public_url,
            'languages_known': languages_known,
            'phone': phone,
            'skills': skills,
            'education': educations,
            'experience': experiences,
            'payment_status':False,
        }

        resume_ref.set(resume_data)

        resume_id = resume_ref.id

        return redirect('resume_preview', resume_id = resume_id)
    return render(request,'main/index.html')


def resume_preview(request, resume_id):
    resume_ref = db.collection('resumes').document(resume_id)
    if resume_ref.get().exists:
        resume_details = resume_ref.get().to_dict()
        resume_details['id'] = resume_id
        amount = 100  # Set the amount dynamically or based on your requirements
        order_id = initiate_payment(amount)
        print(order_id)
        context = {
            'order_id': order_id,
            'amount': amount,
            'resume' : resume_details,
            'RAZORPAY_API_KEY':os.getenv('RAZORPAY_API_KEY')
        }
        return render(request, 'main/resume_preview.html', context)
    
    return HttpResponse('Something went wrong.Try Again Later')

@csrf_exempt
def payment_process(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        resume_id = body_data.get('resume_id')

        print(body_data)

        resume_ref = db.collection('resumes').document(resume_id)
        params_dict = body_data.get('response1')
        print(params_dict)

        try:
            status = client.utility.verify_payment_signature(params_dict)
            if status:
                if resume_ref.get().exists:
                    resume_ref.update({
                        'payment_status':True,
                        'payment_id':params_dict.get('razorpay_payment_id')
                })
                return JsonResponse({
                    'status':'true',
                    'resume_id':resume_id
                })
            else:
                return JsonResponse({
                    'status':'false',
                    'resume_id':resume_id,
                    'payment_id':params_dict.get('razorpay_payment_id'),
                })
        except:
            return JsonResponse({
                    'status':'failed',
                    'resume_id':resume_id
            })
    else:
        return JsonResponse({
                    'status':'failed',
                    'resume_id':resume_id
        })

def initiate_payment(amount, currency='INR'):
    data = {
        'amount': amount * 100,
        'currency': currency,
        'payment_capture': '1'
    }
    response = client.order.create(data=data)
    return response['id']


def payment_success(request, resume_id):
    resume_ref = db.collection('resumes').document(resume_id)
    resume_details = resume_ref.get().to_dict()
    return render(request, 'main/resume_download.html', {'resume': resume_details})
    

def payment_failed(request):
    return render(request, 'main/payment_failed.html')