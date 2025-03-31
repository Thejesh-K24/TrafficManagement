from django.shortcuts import render  # Import render
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserData  # Import your model
from django.contrib.auth import authenticate, login as auth_login
from .models import TrafficData
from .models import TrafficData  # Import your model
from .trafficsense import TrafficSense  # Import TrafficSense class
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import boto3
from django.conf import settings    
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json

def home(request):
    traffic_data = TrafficData.objects.all()
    return render(request, 'index.html', {'traffic_data': traffic_data})

# Initialize AWS clients
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)

sns_client = boto3.client(
    "sns",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)

def upload_to_s3(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        file_name = file.name

        # Upload file to S3
        s3_client.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file_name)

        # Publish to SNS after successful upload
        sns_message = f"New file uploaded: {file_name}"
        sns_client.publish(
            TopicArn=settings.AWS_SNS_TOPIC_ARN,
            Message=sns_message,
            Subject="New Traffic Data Uploaded"
        )

        return HttpResponse(f"File {file_name} uploaded successfully and notification sent!")

    return render(request, "upload.html")

#logic for delete the traffic data
@csrf_exempt
def delete_traffic_data(request, data_id):
    """Deletes a traffic data entry."""
    traffic_record = get_object_or_404(TrafficData, id=data_id)
    traffic_record.delete()
    return redirect('index')

#logic for update the traffic data

@csrf_exempt
def update_traffic_data(request, data_id):
    """Updates traffic data, stores it in S3, and triggers SNS notification."""
    traffic_record = get_object_or_404(TrafficData, id=data_id)

    if request.method == "POST":
        new_vehicle_count = request.POST.get('number_of_vehicles')

        if new_vehicle_count.isdigit():
            traffic_record.number_of_vehicles = int(new_vehicle_count)
            traffic_record.save()

            # Prepare JSON data for S3
            traffic_data = {
                "junction_id": traffic_record.junction_id,
                "number_of_vehicles": traffic_record.number_of_vehicles,
            }
            file_name = f"traffic_update_{traffic_record.id}.json"

            try:
                # Upload traffic data JSON to S3
                s3_client.put_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=file_name,
                    Body=json.dumps(traffic_data),
                    ContentType="application/json"
                )

                # Publish SNS Notification
                sns_message = f"Traffic update at {traffic_record.junction_id}: {traffic_record.number_of_vehicles} vehicles."
                sns_client.publish(
                    TopicArn=settings.AWS_SNS_TOPIC_ARN,
                    Message=sns_message,
                    Subject="Traffic Update Alert"
                )

                messages.success(request, "Traffic data updated and stored in S3 successfully!")
            except Exception as e:
                messages.error(request, f"Failed to update AWS services: {str(e)}")

        else:
            messages.error(request, "Invalid vehicle count.")

        return redirect('index')

    return render(request, 'update.html', {'traffic_record': traffic_record})

#logic for signup the appplication
def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Password and Confirm Password do not match.")
            return render(request, "signup.html")

        # Save the user if passwords match
        user = UserData(name=name, email=email, password=password)
        user.save()

        messages.success(request, "Signup successful! You can now log in.")
        return redirect("login")

    return render(request, "signup.html")


#For Login to application
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Check if the user exists in UserData model with the provided username and password
        user = UserData.objects.filter(name=username, password=password).first()

        if user:  # User exists and password matches
            # Manually create a session for the user
            request.session['user_id'] = user.id  # Store the user ID (or any other info) in the session
            request.session['is_logged_in'] = True  # Optionally, set a flag to indicate that the user is logged in
            request.session['username'] = user.name

            a =  request.session['username'] = user.name
            print("------->>>", a)
            
            return redirect('traffic_update')  # Redirect to the desired page after successful login
        else:
            messages.error(request, "Invalid username or password")  # Show error message for failed login
    
    return render(request, 'login.html')


#Logic to update the traffic data
@csrf_exempt
def traffic_update(request, data_id):
    """Updates traffic data, stores it in S3, and triggers SNS notification."""
    traffic_record = get_object_or_404(TrafficData, id=data_id)

    if request.method == "POST":
        new_vehicle_count = request.POST.get('number_of_vehicles')

        if new_vehicle_count.isdigit():
            traffic_record.number_of_vehicles = int(new_vehicle_count)
            traffic_record.save()

            # Prepare JSON data for S3
            traffic_data = {
                "junction_id": traffic_record.junction_id,
                "number_of_vehicles": traffic_record.number_of_vehicles,
            }
            file_name = f"traffic_update_{traffic_record.id}.json"

            try:
                # Upload traffic data JSON to S3
                s3_client.put_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=file_name,
                    Body=json.dumps(traffic_data),
                    ContentType="application/json"
                )

                # Publish SNS Notification
                sns_message = f"Traffic update at Junction {traffic_record.junction_id}: {traffic_record.number_of_vehicles} vehicles."
                sns_client.publish(
                    TopicArn=settings.AWS_SNS_TOPIC_ARN,
                    Message=sns_message,
                    Subject="Traffic Update Alert"
                )

                messages.success(request, "Traffic data updated and stored in S3 successfully!")
            except Exception as e:
                messages.error(request, f"Failed to update AWS services: {str(e)}")

        else:
            messages.error(request, "Invalid vehicle count.")

        return redirect('index')

    return render(request, 'update.html', {'traffic_record': traffic_record})

# To logout
def logout(request):
    # Clear specific session variables
    if 'user_id' in request.session:
        del request.session['user_id']
    
    if 'is_logged_in' in request.session:
        del request.session['is_logged_in']
    
    # Optionally, flush the entire session
    request.session.flush()
    
    return redirect('index')





