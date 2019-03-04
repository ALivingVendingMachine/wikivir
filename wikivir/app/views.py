from django.shortcuts import render, redirect
from .models import MalwareSample
from .forms import MalwareSampleForm
from hashlib import sha256
from django.core.files.storage import FileSystemStorage

# Create your views here.
def index(request):
    cont = {}
    if request.method == 'POST':
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
                sample = form.save(commit=False)
                sample.fileHash = hashed
                sample.filePath = '/samples/'+hashed
                fs = FileSystemStorage(location=sample.filePath)
                fs.save(sample.fileHash, file)
                sample.save()
                print("nice")
                print("saved, redirect")
                return redirect("index")
            else:
                print("invalid")
            return redirect("index")
        else:
            print("Already existed")

        print("stong post")
        print("Got file lol")
    else:
        print("nice get m8")

    form = MalwareSampleForm()
    cont = {
        "form": form,
    }

    return render(request, 'index.html', cont)
