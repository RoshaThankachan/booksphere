from django.contrib import admin
from .models import Group, Sharing, Discussion

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    filter_horizontal = ('members',)

@admin.register(Sharing)
class SharingAdmin(admin.ModelAdmin):
    list_display = ('book', 'owner', 'available_for_loan')

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'created_at')
