from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from imagekit.models import ImageModel
from django.utils.hashcompat import sha_constructor
from django.core.mail import mail_admins, send_mail
from django.contrib.sites.models import Site
from django.template import Context, loader

import flickrapi
import re
import os
import datetime
import random

SHA1_RE = re.compile('^[a-f0-9]{40}$')

def flicker_callback(progress, done):
    """
    Used to look like this:
    def func(progress, done):
                ...:         if done:
                ...:             print "Done uploading"
                ...:     else:
                ...:             print "At %s%%" % progress
                ...: 
    
    """
    if done:
        return True
    else:
        return False
    
def get_image_path(instance, filename):
    return os.path.join('origs', re.sub(r'[\s\t-\(\)\*\%\$\#\@\!\&]', '_', os.path.split(filename)[1]))
    
class Image(ImageModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=get_image_path,max_length=255)
    description = models.CharField(max_length=255)
    tags = models.CharField(max_length=255,default="dna11, dna portrait, dna, canvas")
    pub_date = models.DateField(auto_now_add=True)
    num_views = models.PositiveIntegerField(editable=False, default=0)
    
    class Meta:
        ordering = ["name"]
        
    class IKOptions:
        spec_module = 'sharepic.specs'
        cache_dir = 'pcache'
        image_field = 'image'
        save_count_as = 'num_views'
    
    def __unicode__(self):
        return self.name
        
    def admin_thumbnail(self):
        return u'<img src="%s">' % (self.admin_thumb.url)
    admin_thumbnail.short_description = 'Thumbnail'
    admin_thumbnail.allow_tags = True
    
def get_client_image_path(instance, filename):
    #'%s_%s' % (instance.client.first_name.lower(),instance.client.last_name.lower()),
    return os.path.join('client_uploads', re.sub(r'[\s\t-\(\)\*\%\$\#\@\!\&]', '_', os.path.split(filename)[1]))
    
class ClientImage(ImageModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=get_client_image_path,max_length=255)
    pub_date = models.DateField(auto_now_add=True)
    num_views = models.PositiveIntegerField(editable=False, default=0)
    
    class Meta:
        ordering = ["name"]
        
    class IKOptions:
        spec_module = 'sharepic.client_specs'
        cache_dir = 'pcache'
        image_field = 'image'
        save_count_as = 'num_views'
    
    def __unicode__(self):
        return self.name
        
    def admin_thumbnail(self):
        return u'<img src="%s">' % (self.admin_thumb.url)
    admin_thumbnail.short_description = 'Thumbnail'
    admin_thumbnail.allow_tags = True    
    
class Client(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField()
    added = models.DateField(auto_now_add=True)
    send_email = models.BooleanField()
    is_published = models.BooleanField()
    pub_date = models.DateTimeField(blank=True,null=True)
    photos = models.ManyToManyField('Image',related_name='galleries',blank=True,null=True)
    client_uploads = models.ManyToManyField('ClientImage',related_name='clientgal',blank=True,null=True)
    key = models.CharField(max_length=40,blank=True)
    key_issued = models.DateTimeField(blank=True,null=True)
        
    class Meta:
        ordering = ["email"]
    
    def __unicode__(self):
        return self.email
    
    def public(self):
        return self.photos.all()
        
    def client_uploaded(self):
        return self.client_uploads.all()
        
    def all_pics(self):
        pre = self.photos.all()
        aft = self.client_uploads.all()
        ret = []
        for p in pre:
            ret.append(p)
        for a in aft:
            ret.append(a)
        return ret
        
    def auth_key_expired(self,key):
        expiration_date = datetime.timedelta(hours=settings.KEY_LIFE_HOURS)
        return self.key != key or (self.key_issued + expiration_date <= datetime.datetime.now())
    auth_key_expired.boolean = True
    
    def create_key(self, user):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        self.key = sha_constructor(salt+user).hexdigest()
        self.key_issued = datetime.datetime.now()
        self.save()
        return self
    
    def publish(self,client):
        if self.is_published == False:
            self.is_published = True
            self.pub_date = datetime.datetime.now()
            self.save()
            if settings.FLICKR:
                flickr = flickrapi.FlickrAPI(settings.FLICKR_API_KEY, settings.FLICKR_API_SECRET, token=settings.FLICKR_TOKEN)
                for p in self.photos.all():
                    res = flickr.upload(filename=settings.MEDIA_ROOT + str(p.image), title=p.name, description=p.description, tags=p.tags, callback=flicker_callback)
               
    def save(self):
        if self.send_email:
            self.send_email = False
            self.create_key(self.email)
            site = Site.objects.get(id=settings.SITE_ID)
            t = loader.get_template('emails/registration.txt')
            c = Context({ 'object': self,'site': site })
            
            message = t.render(c)
            send_mail('Your art from %s is waiting for you!' % site.name,message,settings.DEFAULT_FROM_EMAIL,[self.email,])   
            
        super(Client, self).save()    

