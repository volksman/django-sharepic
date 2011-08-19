from sharepic.models import Image, Client, ClientImage
from sharepic.forms import ClientImageModelForm, AuthForm
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.core.mail import mail_admins, send_mail
from django.core.cache import cache
import logging
import re

SHA1_RE = re.compile('^[a-f0-9]{40}$')
SPECS = ['desktop_large','desktop_large_wide','desktop_medium','avatar']
CURRENT_SITE = Site.objects.get(id=settings.SITE_ID)
    
def newshare(request):
    if request.method == 'POST':
        form = ClientImageModelForm(request.POST, request.FILES)
        if form.is_valid():
            new = form.save(commit=False)
            try: 
                profile = Client.objects.get(key=request.session['key'])
            except:
                #no user
                return HttpResponseNotFound("no user %s" % request.session['key'])
            if request.session.get('key') and not profile.auth_key_expired(request.session['key']):
                new.save()
                profile.client_uploads.add(new.id)
            else:
                return HttpResponseNotFound("not allowed")
            
            return HttpResponseRedirect('/shareit/%s_%s' % (profile.first_name.lower(), profile.last_name.lower()))
    return HttpResponseNotFound('not post or not valid')

def showshare(request,uri):    
    try:       
        f,l = uri.split("_")
    except:
        return HttpResponseNotFound("not found?")
        
    profile = get_object_or_404(Client, first_name=f, last_name=l, is_published=True)
    
    if request.session.get('key') and not profile.auth_key_expired(request.session['key']):
        profile.key = True
        profile.pics = []
        photos = profile.public()
        for p in photos:
            for l in SPECS:
                profile.pics.append({
                    'type': l.replace("_"," "),
                    'url': p.__getattribute__(l).url,
                    'size': str(p.__getattribute__(l).width) + "x" + str(p.__getattribute__(l).height)
                })
        
    else:
        profile.key = False
    
    return render_to_response('sharepic/show_share.html', { 'profile': profile, 'auth': AuthForm(), 'uploadform': ClientImageModelForm() })

def remove_image(request,uri):
    try:
        profile = Client.objects.get(key=request.session['key'])
    except:
        return HttpResponseNotAllowed()
        
    image = get_object_or_404(ClientImage, pk=uri)
    
    if request.session.get('key') and not profile.auth_key_expired(request.session['key']):
        image.delete()
        
    return HttpResponseRedirect('/shareit/%s_%s' % (profile.first_name.lower(),profile.last_name.lower()))

def remove_share(request,uri):
    try:       
        f,l = uri.split("_")
    except:
        return HttpResponseNotFound("not found?")
        
    profile = get_object_or_404(Client, first_name=f, last_name=l, is_published=True)
    if request.session.get('key') and not profile.auth_key_expired(request.session['key']):
        profile.is_published = False
        profile.save()
        
    return render_to_response('sharepic/remove_share.html', { })
    
def authuser(request,key):
    if SHA1_RE.search(key):
        try:
            profile = Client.objects.get(key=key)
        except:    
            return HttpResponseRedirect('/shareit/request_key/')
        
        if profile.auth_key_expired(key):
            return HttpResponseRedirect('/shareit/request_key/')
        else:
            profile.publish(profile)
            request.session['key'] = key
            return HttpResponseRedirect('/shareit/%s_%s' % (profile.first_name.lower(),profile.last_name.lower()))
            
    return HttpResponseRedirect('/shareit/request_key/')

def logout(request):
    if request.session.get('key'):
        del request.session['key']
    if request.method == 'GET':
        try:
            redir = request.GET['next']
            return HttpResponseRedirect(redir)
        except:
            pass
    return HttpResponseRedirect('/shareit/request_key/')

def request_key(request):
    return render_to_response('sharepic/request_key.html', { 'form': AuthForm() })

def send_key(request):
    # Add code to count how many times a user has attempted a new key.  Set a max and lock out.
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            try:
                addy = Client.objects.get(email=form.cleaned_data['email'])
            except:
                return render_to_response('sharepic/request_key_nokey.html', {'form': form, 'message': 'No address found' } )
            
            key = addy.create_key(addy.email)
            
            send_mail('New authentication key.',
                      "You, or someone posing as you, requested access to your profile page on %s.\n\nHere is your new key:\n\nhttp://%s/shareit/%s" % (CURRENT_SITE.name,CURRENT_SITE.domain,addy.key), settings.DEFAULT_FROM_EMAIL, [addy.email,])
            
            mail_admins('Key',addy.key) 
            return render_to_response('sharepic/request_key_approved.html')
    return render_to_response('sharepic/request_key_nokey.html', {'form': form } )

def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_id = None
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    if progress_id:
        from django.utils import simplejson
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        json = simplejson.dumps(data)
        return HttpResponse(json)
    else:
        return HttpResponseBadRequest('Server Error: You must provide X-Progress-ID header or query param.')

