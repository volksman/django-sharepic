from django.contrib import admin
from sharepic.models import Image, Client, ClientImage

class ClientImageAdmin(admin.ModelAdmin):
    list_display = ['name','pub_date','admin_thumbnail']
    list_display_links = ['pub_date','admin_thumbnail']
    list_filter = ['pub_date',]
    list_editable = ['name',]
    search_fields = ['name',]

class ImageAdmin(admin.ModelAdmin):
    list_display = ['name','pub_date','admin_thumbnail']
    list_display_links = ['pub_date','admin_thumbnail']
    list_filter = ['pub_date',]
    list_editable = ['name',]
    search_fields = ['name',]

class ClientAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'added', 'is_published' ]
    list_filter = ['added','is_published','pub_date' ]
    list_editable = [ 'first_name', 'last_name' ]
    search_fields = ['email', 'first_name', 'last_name', ]
    filter_horizontal = ['photos','client_uploads']

admin.site.register(Client,ClientAdmin)
admin.site.register(Image,ImageAdmin)
admin.site.register(ClientImage,ClientImageAdmin)