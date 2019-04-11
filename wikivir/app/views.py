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

fields = [
    'fileHash',
    'fileBlob',
    'date',
    'ready',
    'file',
    'readelf',
    'objdump',
    'tags',
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

    cont = {
        'topic': topicEntry.topicTitle,
        'topicBody': topicEntry.topicBody,
    }

    return render(request, 'topicView.html', cont) 

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
            if key in fields:
                setattr(sample, key, str(value))
        
        sample.save()
        return JsonResponse({"status": "good"})

    obj = {}

    try:
        sample = MalwareSample.objects.get(fileHash=sampleHash)
    except MalwareSample.DoesNotExist:
        return JsonResponse({"err": str(sampleHash) + " does not exist", "status": "err"})
    
    obj['fileHash'] = sample.fileHash
    obj['date'] = sample.date
    obj['ready'] = sample.ready
    obj['file'] = sample.file
    obj['readelf'] = sample.readelf
    obj['objdump'] = sample.objdump
    obj['tags'] = list(sample.tags.names())
    return JsonResponse(obj)

def addTag(request, sampleHash):
    if request.method == "POST":
        print("got it")
        try:
            sample = MalwareSample.objects.get(fileHash=sampleHash)
        except MalwareSample.DoesNotExist:
            return redirect(sampleView, sampleHash)

        for key, value in request.POST.dict().items():
            if key == "tags":
                sample.tags.add(value)
        
        sample.save()
        return redirect(sampleView, sampleHash)
    return redirect(sampleView, sampleHash)

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
        'module': mod,
    }

    return render(request, 'editView.html', cont)

def editTopic(request, topic):

    return JsonResponse({'err':'not impl'})

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


