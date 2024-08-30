from django.contrib import admin
from django.contrib.auth.models import Group, User
from . models import Profile, Tweet
# Unregister Group model
admin.site.unregister(Group)

# Mix profile into User
class ProfileInline(admin.StackedInline):
    model = Profile

# Extend User model
class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ['username']
    inlines = [ProfileInline]

# Unregister User model
admin.site.unregister(User)

# Register User and profile models here.
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Tweet)




