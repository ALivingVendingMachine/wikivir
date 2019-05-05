from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import MalwareSample
from .models import Topic
from .forms import MalwareSampleForm
from hashlib import sha256
from django.core.files.storage import FileSystemStorage
import threading
import subprocess
import sys
import bleach

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
    #TODO: sanitize topic, probably
    try:
        topicEntry = Topic.objects.get(topicTitle=topic)
    except Topic.DoesNotExist:
        return redirect('topicNotFound', topic=topic)

    #cont = {
    #    'topic': topicEntry.topicTitle,
    #    'topicBody': topicEntry.topicBody,
    #}

    return render(request, 'topicView.html', {}) 

def topicNotFound(request, topic):
    cont = {
        "topic": topic,
    }

    return render(request, 'topicNotFound.html', cont)

def apiSample(request, sampleHash):
    if request.method == "POST":
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

def apiTopic(request, topic):
    if request.method == "POST":
        print("got it")
        try:
            top = Topic.objects.get(topicTitle=topic)
        except MalwareSample.DoesNotExist:
            return JsonResponse({"err": str(topic) + " does not exist", "status":"err"})

        print(request.POST.dict())

        for key, value in request.POST.dict().items():
            print("looking for " + key)
            if key == "topicBody":
                top.topicBody = value
            if key == "topicTitle":
                top.topicTitle = value
       
        top.save()
        return JsonResponse({"status": "good"})

    obj = {}

    try:
        top = Topic.objects.get(topicTitle=topic)
    except Topic.DoesNotExist:
        return JsonResponse({"err": str(topic) + " does not exist", "status": "err"})

    obj['topicTitle'] = bleach.clean(top.topicTitle)
    obj['topicBody'] = bleach.clean(top.topicBody)
    obj['category'] = bleach.clean(top.category)
    obj['status'] = "good"
    return JsonResponse(obj)

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
        cmd.append(str("/samples/" + check.fileBlob.name))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        proc.wait()
        proc.stdout.flush()
        out = str(proc.communicate()[0].decode('utf-8'))
        if cmd[0] == 'file':
            print(out)
        setattr(check, cmd[0], str(out))
    
    check.ready = True
    check.save()
