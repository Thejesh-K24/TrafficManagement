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

def home(request):
    traffic_data = TrafficData.objects.all()
    return render(request, 'index.html', {'traffic_data': traffic_data})


@csrf_exempt
def delete_traffic_data(request, data_id):
    """Deletes a traffic data entry."""
    traffic_record = get_object_or_404(TrafficData, id=data_id)
    traffic_record.delete()
    return redirect('index')

def update_traffic_data(request, data_id):
    """Updates traffic data."""
    traffic_record = get_object_or_404(TrafficData, id=data_id)

    if request.method == "POST":
        new_vehicle_count = request.POST.get('number_of_vehicles')
        if new_vehicle_count.isdigit():
            traffic_record.number_of_vehicles = int(new_vehicle_count)
            traffic_record.save()
        return redirect('index')

    return render(request, 'update.html', {'traffic_record': traffic_record})
   

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
        user = UserData(name=name, email=email, password=password)  # Ensure User model has these fields
        user.save()

        messages.success(request, "Signup successful! You can now log in.")
        return redirect("login")  # Change to the appropriate login page

    return render(request, "signup.html")



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


def traffic_update(request):
    if request.method == 'POST':
        # Extract data from the POST request
        junction_id = request.POST.get('Junction')
        number_of_vehicles = request.POST.get('Number_vehicle')

        # Validate data (for example, ensure number_of_vehicles is an integer)
        try:
            number_of_vehicles = int(number_of_vehicles)
        except ValueError:
            messages.error(request, "Please enter a valid number for the number of vehicles.")
            return redirect('traffic_update')  # Redirect back to the traffic_update page

        # Create and save the TrafficData object
        traffic_data = TrafficData(junction_id=junction_id, number_of_vehicles=number_of_vehicles)
        traffic_data.save()

        # Add a success message
        messages.success(request, 'Traffic data has been successfully updated!')

        # Redirect to the home or other desired page
        return redirect('index')  # You can change 'index' to any view you prefer

    # If it's a GET request, simply render the traffic_update page
    return render(request, 'traffic_update.html')



def logout(request):
    # Clear specific session variables
    if 'user_id' in request.session:
        del request.session['user_id']
    
    if 'is_logged_in' in request.session:
        del request.session['is_logged_in']
    
    # Optionally, flush the entire session
    request.session.flush()
    
    return redirect('index')
