from django.shortcuts import render, redirect
from .models import MalwareSample
from .models import Topic
from .forms import MalwareSampleForm
from hashlib import sha256
from django.core.files.storage import FileSystemStorage

# Create your views here.

# Index
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

            form = MalwareSampleForm(request.POST, request.FILES)
            if form.is_valid():
                # setup form
                sample = form.save(commit=False)
                sample.fileHash = hashed
                sample.filePath = '/samples/'+hashed

                # save file
                fs = FileSystemStorage(location=sample.filePath)
                fs.save(sample.fileHash, file)

                # save form
                sample.save()

                # done
                print("nice")
                print("saved at ", sample.filePath, ", redirect")
                return redirect(sampleView, sampleHash=hashed)
            else:
                # something when wrong
                print("invalid")
            return redirect("index")
        else:
            # we already have it
            print("Already existed, redirect")
            return redirect(sampleView, sampleHash=hashed)

        print("stong post")
        print("Got file lol")
    else:
        print("GET index")

    form = MalwareSampleForm()
    cont = {
        "form": form,
    }

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

    form = MalwareSampleForm()
    cont = {
        "form": form,
    }

    #TODO: sanitize sampleHash

    try:
        check = MalwareSample.objects.get(fileHash=sampleHash)
    except MalwareSample.DoesNotExist: # effectively we should 404 here
        return redirect('sampleNotFound', sampleHash=sampleHash)

    print(check)
    print('got it?')
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