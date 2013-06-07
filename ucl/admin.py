from django.contrib import admin
from models import Member, Session
from models import Author, Book
from models import Collection, CollectionBook


from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class MemberInline(admin.StackedInline):
    model = Member
    can_delete = False


class UserAdmin(UserAdmin):
    inlines = [MemberInline]


#class SessionAdmin(admin.ModelAdmin):

admin.site.register(Member)
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Collection)
admin.site.register(CollectionBook)
admin.site.register(Session)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)