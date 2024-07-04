from django.shortcuts import render, redirect,HttpResponse
from django.views.decorators.csrf import csrf_protect
from firestoreconfig import db
import magic
import firebase

def home(request):
    return render(request,'main/index.html')

def header(request):
    return render(request,'main/header.html')

@csrf_protect
def create_cv(request):
    if request.method == 'POST':
        # Process form data
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
        educations = []

        # Process experiences and educations as per your existing logic
        for key in request.POST:
            if key.startswith('experiences['):
                index = key.split('[')[1].split(']')[0]
                if index.isdigit():
                    index = int(index)
                    while len(experiences) <= index:
                        experiences.append({})
                    experiences[index][key.split('][')[1].split(']')[0]] = request.POST[key]

            if key.startswith('educations['):
                index = key.split('[')[1].split(']')[0]
                if index.isdigit():
                    index = int(index)
                    while len(educations) <= index:
                        educations.append({})
                    educations[index][key.split('][')[1].split(']')[0]] = request.POST[key]

        # Upload profile photo to Firebase Storage
        # if profile_photo:
        #     mime = magic.Magic(mime=True)
        #     mime_type = mime.from_buffer(profile_photo.read())
        #     profile_photo.seek(0)

        #     bucket = firebase.storage().bucket()
        #     blob = bucket.blob(f'profile_photos/{profile_photo.name}')
        #     blob.upload_from_file(profile_photo, content_type=mime_type)
        #     blob.make_public()

        #     profile_photo_url = blob.public_url
        # else:
        #     profile_photo_url = None

        # Create resume data dictionary
        resume_data = {
            'first_name': first_name.upper(),
            'last_name': last_name.upper(),
            'contact_info': contact_info,
            'email_web': email_web,
            'website': website,
            # 'profile_photo': profile_photo_url,
            'languages_known': languages_known,
            'phone': phone,
            'skills': skills,
            'education': educations,
            'experience': experiences,
            'payment_status':True,
        }

        # Store resume data in Realtime Database
        resume_ref = db.child('resumes').push(resume_data)


        resume_id = resume_ref['name']  # Get the unique key of the newly added data
        print(resume_id)

        return redirect('resume_preview', resume_id=resume_id)

    return render(request, 'main/index.html')


def resume_preview(request, resume_id):
    # print(resume_id)
    resume_ref = db.child('resumes').child(resume_id).get()
    
    if resume_ref.val():
        resume_details = resume_ref.val()
        print(resume_details)
        resume_details['id'] = resume_id
        return render(request, 'main/resume_preview.html', {'resume': resume_details})
    
    return HttpResponse('Something went wrong. Try Again Later')


def process_payment(request, resume_id):
    # Integrate with your payment gateway here
    return redirect('payment_success', resume_id=resume_id)

def verify_payment(request):
    return True

def payment_success(request, resume_id):
    resume_ref = db.child('resumes').child(resume_id).get()
    
    if verify_payment(request):
        # resume_ref.update({
        #     'payment_status': True,
        # })
        resume_details = resume_ref.val()
        # print(resume_details)
        return render(request, 'main/resume_download.html', {'resume': resume_details})
    
    return redirect('payment_failed')



def payment_failed(request):
    return render(request, 'main/payment_failed.html')