from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . models import Profile, Tweet
from .forms import TweetForm, SignUpForm, ProfilePicForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


# Create your views here.
def home(request):
    if request.user.is_authenticated:
        form = TweetForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                tweet = form.save(commit=False)
                tweet.user = request.user
                tweet.save()
                messages.success(request, 'Tweet has been posted.')
                return redirect('home')
        profiles = Profile.objects.exclude(user=request.user)
        tweets = Tweet.objects.all().order_by('-created_at')
        return render(request, 'home.html', {
            'tweets': tweets,
            'form': form,
            'profiles': profiles,
        })
    else:
        tweets = Tweet.objects.all().order_by('-created_at')
        return render(request, 'home.html', {'tweets': tweets})

def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {'profiles' : profiles})
    else:
        messages.success(request, "You need to be logged in to view this page....")
        return redirect("home")

def profile(request, pk):
    if request.user.is_authenticated:
        tweets = Tweet.objects.filter(user_id = pk).order_by('-created_at')
        profile= Profile.objects.get(user_id = pk)

        # Post form logic
        if request.method == "POST":
            # get current user
            current_user_profle = request.user.profile
            # get form data
            action = request.POST['follow']
            # decide to follow or unfollow
            if action == 'unfollow':
                current_user_profle.follows.remove(profile)
            else:
                current_user_profle.follows.add(profile)
            
            # save the current profile
            current_user_profle.save()



        return render(request, 'profile.html', {'profile': profile, 'tweets': tweets})
    else:
        messages.success(request, "You need to be logged in to view this page....")
        return redirect("home")
    
def unfollow(request, pk):
	if request.user.is_authenticated:
		# Get the profile to unfollow
		profile = Profile.objects.get(user_id=pk)
		# Unfollow the user
		request.user.profile.follows.remove(profile)
		# Save our profile
		request.user.profile.save()
		# Return message
		messages.success(request, (f"You Have Successfully Unfollowed {profile.user.username}"))
		return redirect(request.META.get("HTTP_REFERER"))

	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')
     

def follow(request, pk):
	if request.user.is_authenticated:
		# Get the profile to unfollow
		profile = Profile.objects.get(user_id=pk)
		# Unfollow the user
		request.user.profile.follows.add(profile)
		# Save our profile
		request.user.profile.save()

		# Return message
		messages.success(request, (f"You Have Successfully Followed {profile.user.username}"))
		return redirect(request.META.get("HTTP_REFERER"))

	else:
		messages.success(request, ("You Must Be Logged In To View This Page..."))
		return redirect('home')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in successfully....")
            return redirect('home')
        else:
            messages.success(request, "There is an error with login. Please try again later!")
            return redirect('login')
    else:
        return render(request, 'login.html')
    



def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out!!!")
    return redirect('login')



def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # first_name = form.cleaned_data['first_name']
			# last_name = form.cleaned_data['second_name']
			# email = form.cleaned_data['email']
            # Log in user
            user = authenticate(username=username, password=password, )
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully registered! Welcome!")
                return redirect('home')
            else:
                messages.error(request, "There was a problem logging you in. Please try again.")
                return redirect('login')  # Redirect to the login page or handle accordingly
        else:
            messages.error(request, "There was a problem while registering. Please check the form and try again.")
    
    return render(request, "register.html", {'form': form})

def update_user(request):
	if request.user.is_authenticated:
		current_user = User.objects.get(id=request.user.id)
		profile_user = Profile.objects.get(user__id=request.user.id)
		# Get Forms
		user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)
		profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()

			login(request, current_user)
			messages.success(request, ("Your Profile Has Been Updated!"))
			return redirect('home')

		return render(request, "update_profile.html", {'user_form':user_form, 'profile_form':profile_form})
	else:
		messages.success(request, ("You Must Be Logged In To View That Page..."))
		return redirect('home')
     

def tweet_like(request, pk):
     if request.user.is_authenticated:
          tweet = get_object_or_404(Tweet, id=pk)
          if tweet.likes.filter(id = request.user.id):
               tweet.likes.remove(request.user)
          else:
               tweet.likes.add(request.user)
          return redirect(request.META.get('HTTP_REFERER'))          
          
     else:
        messages.success(request, ("You Must Be Logged In To View That Page..."))
        return redirect('home')       

def tweet_share(request, pk):
        tweet = get_object_or_404(Tweet, id=pk)
        if tweet:
            return render(request, 'share_tweet.html', {'tweet': tweet})
        else:
            messages.success(request, ("Sorry that tweet doesn't exist..."))
            return redirect('home')
        
def delete_tweet(request, pk):
     if request.user.is_authenticated:
          tweet = get_object_or_404(Tweet, id=pk)
          if request.user.username == tweet.user.username:
               tweet.delete()
               messages.success(request, ('Tweet has been deleted!'))
               return redirect('profile', pk=request.user.profile.id)
          else:
            messages.success(request, ("You Must Be Logged In To View That Page..."))
            return redirect('home') 
               
     else:
        messages.success(request, ("You Must Be Logged In To View That Page..."))
        return redirect('home') 
        
def edit_tweet(request, pk):
    tweet = get_object_or_404(Tweet, id=pk)

    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to edit a tweet.")
        return redirect('login')  # Redirect to login if the user is not authenticated

    if request.method == 'POST':
        form = TweetForm(request.POST, instance=tweet)
        if form.is_valid():
            form.save()  # Save the form directly
            messages.success(request, "Your tweet has been updated.")
            return redirect('profile', pk=request.user.profile.id)  # Redirect to the profile page
        else:
            # Render form with errors
            return render(request, 'edit_tweet.html', {'form': form, 'tweet': tweet})

    # Handle GET requests
    form = TweetForm(instance=tweet)
    return render(request, 'edit_tweet.html', {'form': form, 'tweet': tweet})


def search(request):
     if request.method == 'POST':
          search = request.POST['search']
          searched = Tweet.objects.filter(body__contains = search)
          return render(request, 'search.html', {'search': search, 'searched' : searched})
     else:
          return render(request, 'search.html')