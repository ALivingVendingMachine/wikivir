from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import MalwareSample
from .models import Topic
from .forms import MalwareSampleForm
from hashlib import sha256
from django.core.files.storage import FileSystemStorage
import threading
import subprocess
import sys
import bleach
import json
import urllib

# Create your views here.

fieldsMalware = [
    'fileHash',
    'fileBlob',
    'date',
    'ready',
    'file',
    'readelf',
    'objdump',
]

fieldsTopic = [
    'topicTitle',
    'topicBody',
    'relatedSamples',
    'category',
]

def index(request):
    cont = {}
    if request.method == 'POST':
        print("POST index")
        print(request.FILES)
        file = request.FILES['file']
        buf = file.read()

        hasher = sha256()
        hasher.update(buf)
        hashed = str(hasher.hexdigest())

        try:
            check = MalwareSample.objects.get(fileHash=hashed)
        except MalwareSample.DoesNotExist: #this means we want the file
            print("did not exist!")

            # setup form
            model = MalwareSample()
            model.fileHash = hashed
            model.fileBlob = file
            model.file = "INCOMPLETE"
            model.readelf = "INCOMPLETE"
            model.objdump = "INCOMPLETE"


            model.full_clean()
            model.save()

            #Hell yeah dog, now we're multithreading
            threading.Thread(target=analyzeFile, args=(hashed,)).start()
            #analyzeFile(hashed)

            # done
            print("nice")
            return redirect(sampleView, sampleHash=hashed)
        else:
            # we already have it
            print("Already existed, redirect")
            return redirect(sampleView, sampleHash=hashed)

        print("stong post")
        print("Got file lol")
    else:
        print("GET index")

    return render(request, 'index.html', cont)

# about view
def about(request):
    if request.method != "GET":
        return redirect(index)
    print("GET about")

    return render(request, 'about.html', {})

# sample view
def sampleView(request, sampleHash):
    if request.method != "GET":
        return redirect(index)

    print('GET sampleView')

    #TODO: sanitize sampleHash

    try:
        check = MalwareSample.objects.get(fileHash=sampleHash)
    except MalwareSample.DoesNotExist: # effectively we should 404 here
        return redirect('sampleNotFound', sampleHash=sampleHash)

    cont = {}

    return render(request, 'sampleView.html', cont)

def sampleNotFound(request, sampleHash):
    cont = {
        "sampleHash": sampleHash,
    }
    return render(request, 'sampleNotFound.html', cont)

# topic view
def topicView(request, topic):
    if topic == 'newTE' or topic == 'newAP' or topic == 'newSA':
        return redirect('editTopic', topic=topic)
    try:
        #topicEntry = Topic.objects.get(topicTitle=urllib.parse.quote(topic))
        topicEntry = Topic.objects.get(topicTitle=topic)
    except Topic.DoesNotExist:
        return redirect('topicNotFound', topic=topic)

    cont = {}

    return render(request, 'topicView.html', cont)

def topicNotFound(request, topic):
    cont = {
        "topic": topic,
    }

    return render(request, 'topicNotFound.html', cont)

def apiSample(request, sampleHash):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"err": "user not authenticated", "status": "err"})
        print("got it")
        try:
            sample = MalwareSample.objects.get(fileHash=sampleHash)
        except MalwareSample.DoesNotExist:
            return JsonResponse({"err": str(sampleHash) + " does not exist", "status":"err"})

        print(request.POST.dict())

        for key, value in request.POST.dict().items():
            print("checking for " + key) 
            if key in fieldsMalware:
                setattr(sample, key, bleach.clean(str(value)))
        
        sample.save()
        return JsonResponse({"status": "good"})

    obj = {}
    tops = []

    try:
        sample = MalwareSample.objects.get(fileHash=sampleHash)
    except MalwareSample.DoesNotExist:
        return JsonResponse({"err": str(sampleHash) + " does not exist", "status": "err"})
    
    for top in sample.relatedTopics.all():
        tops.append(bleach.clean(top.topicTitle))

    obj['fileHash'] = bleach.clean(sample.fileHash)
    obj['date'] = sample.date
    obj['ready'] = sample.ready
    obj['file'] = bleach.clean(sample.file)
    obj['readelf'] = bleach.clean(sample.readelf)
    obj['objdump'] = bleach.clean(sample.objdump)
    obj['topics'] = tops
    obj['status'] = "good"
    return JsonResponse(obj)

def apiSampleGetAll(request):
    hashes = []
    for sample in MalwareSample.objects.all():
        hashes.append(sample.fileHash)

    return JsonResponse({"hashes": hashes})

def apiTopic(request, topic):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"err": "user not authenticated", "status": "err"})
        print("got it")
        if topic == 'newTE':
            return easyAddTopic(request, 'TE')
        if topic == 'newAP':
            return easyAddTopic(request, 'AP')
        if topic == 'newSA':
            return easyAddTopic(request, 'SA')
        try:
            top = Topic.objects.get(topicTitle=topic)
        except Topic.DoesNotExist:
            return JsonResponse({'status':'err', 'err':'could not find topic'})

        for key, value in request.POST.dict().items():
            if key == "topicBody":
                top.topicBody = bleach.clean(value)
            if key == "topicTitle":
                value = urllib.parse.quote(value)
                top.topicTitle = value
            if key == "samples":
                value = json.loads(value)
                top.relatedSamples.clear()
                for fileHash in value:
                    try:
                        sample = MalwareSample.objects.get(fileHash = fileHash)
                    except:
                        return JsonResponse({"status":"err", "err":"could not find hash"})
                    top.relatedSamples.add(sample)

        top.save()
        return JsonResponse({"status": "good"})

    obj = {}

    try:
        top = Topic.objects.get(topicTitle=topic)
    except Topic.DoesNotExist:
        return JsonResponse({"err": str(topic) + " does not exist", "status": "err"})

    samps = []
    for samp in top.relatedSamples.all():
        print(samp.fileHash)
        samps.append(bleach.clean(samp.fileHash))

    obj['topicTitle'] = bleach.clean(top.topicTitle)
    obj['topicBody'] = bleach.clean(top.topicBody)
    obj['category'] = bleach.clean(top.get_category_display())
    obj['samples'] = samps
    obj['status'] = "good"
    return JsonResponse(obj)

def easyAddTopic(request, cat):
    top = Topic()
    for key, value in request.POST.dict().items():
        if key == "topicBody":
            top.topicBody = bleach.clean(value)
        if key == "topicTitle":
            top.topicTitle = value

    if top.topicBody == None or top.topicTitle == None or top.topicBody == "" or top.topicTitle == "":
        return JsonResponse({'err': 'could not make topic with empty fields', 'status': 'err'})

    top.save()

    for key, value in request.POST.dict().items():
        if key == "samples":
            value = json.loads(value)
            for fileHash in value:
                try:
                    sample = MalwareSample.objects.get(fileHash = fileHash)
                except:
                    JsonResponse({"status":"err", "err":"could not find hash"})
                top.relatedSamples.add(sample)

    if cat == "TE":
        top.category = "TE"
    elif cat == "AP":
        top.category = "AP"
    elif cat == "SA":
        top.category = "SA"
    top.save()
    return JsonResponse({"status":"good", "msg": "made topic"})



@login_required
def editSample(request, sampleHash, mod):
    if request.method == "POST":
        print(request.POST.dict('content'))
        return redirect(sampleView, sampleHash)
    try:
        check = MalwareSample.objects.get(fileHash=sampleHash)
    except MalwareSample.DoesNotExist: #this means we want the file
        print("analysis failed: did not exist!")
        return redirect(sampleNotFound, sampleHash)

    try:
        module = getattr(check, mod)
    except AttributeError:
        return redirect(sampleNotFound, sampleHash)

    cont = {
        #'content': bleach.clean(module),
        'module': bleach.clean(mod),
    }

    return render(request, 'editView.html', cont)

@login_required
def editTopic(request, topic):
    return render(request, "editTopic.html", {})

def allTopics(request):
    categories = [
        "TE",
        "AP",
        "SA",
    ]

    teList = []
    apList = []
    saList = []

    objects = Topic.objects.all()

    for o in objects:
        if o.category == "TE":
            teList.append(o.topicTitle)
        if o.category == "AP":
            apList.append(o.topicTitle)
        if o.category == "SA":
            saList.append(o.topicTitle)

    cont = {
        "te": teList,
        "ap": apList,
        "sa": saList,
    }

    return render(request, 'allTopics.html', cont)

# user management
# register
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()

    cont = {'form': form}
    return render(request, 'register.html', cont)

def logoutView(request):
    logout(request)
    return redirect(index)

# debug serve view
def debug(request, topic):
    return render(request, 'debug.html', {})

# internal stuff for threading
def analyzeFile(hashed):
    try:
        check = MalwareSample.objects.get(fileHash=hashed)
    except MalwareSample.DoesNotExist: #this means we want the file
        print("analysis failed: did not exist!")
        return

    commands = [
        ['file'],
        ['objdump', '-D'],
        ['readelf', '--all'],
    ]

    for cmd in commands:
        print("running " + cmd[0], flush=True)
        cmd.append(str("/samples/" + check.fileBlob.name))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        print('popen, wait', flush=True)
        proc.wait()
        print('done', flush=True)
        proc.stdout.flush()
        print('flush', flush=True)
        out = str(proc.communicate()[0].decode('utf-8'))
        print('out', flush=True)
        if proc.returncode != 0:
            setattr(check, cmd[0], "Return exit code %d" % (proc.returncode))
        else:
            setattr(check, cmd[0], str(out))
    
    check.ready = True
    check.save()
