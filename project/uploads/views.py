import os, pythoncom, comtypes.client, re
from shutil import copyfile
from django.contrib import messages
from tika import parser
from django.conf import settings
from docx2pdf import convert
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
import csv
from django.http import StreamingHttpResponse
from .forms import UploadForm, FolderUploadForm
from .models import Profile

def home(request):
    form1 = UploadForm()
    form2 = FolderUploadForm()
    obj = Profile.objects.filter().order_by('email')
    if obj.exists():
        dct = {}
        for i in obj:
            dct[i.email] = [i.contact, str(i.cv).replace('\\', '/')]
    else:
        dct = None
    return render(request, "index.html", {"form1": form1, "form2": form2, "obj": dct, "count": obj.count()})

def uploadFile(filetype, filepath):
    if filetype == "pdf":
        newfilepath = filepath
    elif filetype == "docx":
        newfilepath = 'cv/temp.pdf'
        pythoncom.CoInitialize()
        convert(os.path.join(settings.MEDIA_ROOT, filepath), os.path.join(settings.MEDIA_ROOT, newfilepath))
        os.remove(os.path.join(settings.MEDIA_ROOT, filepath))
    elif filetype == "doc" or filetype == "rtf":
        newfilepath = 'cv/temp.pdf'
        pythoncom.CoInitialize()
        wdFormatPDF = 17
        in_file = os.path.join(settings.MEDIA_ROOT, filepath)
        out_file = os.path.join(settings.MEDIA_ROOT, newfilepath)
        word = comtypes.client.CreateObject('Word.Application')
        doc = word.Documents.Open(in_file)
        doc.SaveAs(out_file, FileFormat=wdFormatPDF)
        doc.Close()
        os.remove(os.path.join(settings.MEDIA_ROOT, filepath))
    raw = parser.from_file(os.path.join(settings.MEDIA_ROOT, newfilepath))
    text = raw['content']
    for i in range(0, 10):
        text = text.replace("{0} ".format(i), "{0}".format(i))
    text = text.replace("Email-", "")
    text = text.replace("@ ", "@")
    match1 = re.search(r'[\w\.-]+@[a-z0-9\.-]+', text)
    match2 = re.search("(?:(?:\+|0{0,2})91(\s*[\\-]\s*)?|[0]?)?[789]\d{2}\s*\d{3}\s*\d{4}", text)
    match3 = re.search("([0-9]+(-[0-9]+)+)", text)
    email = match1.group(0)
    if match2:
        contact = match2.group(0)
        contact = ''.join(contact.split(' '))
    elif match3:
        contact = match3.group(0)
        contact = ''.join(contact.split('-'))
    contact = contact[len(contact) - 10:len(contact)]
    finalpath = 'cv\\' + email + '.pdf'
    os.rename(os.path.join(settings.MEDIA_ROOT, newfilepath), os.path.join(settings.MEDIA_ROOT, finalpath))
    return email, contact, finalpath

def uploadUsingDropDown(request):
    if request.method == "POST":
        form1 = UploadForm(request.POST, request.FILES)
        if form1.is_valid():
            files = request.FILES.getlist("files")
            for f in files:
                filetype = str(f).split('.')[-1]
                if filetype == "pdf":
                    filepath = default_storage.save('cv/temp.pdf', f)
                elif filetype == "docx":
                    filepath = default_storage.save('cv/temp.docx', f)
                elif filetype == "doc" or filetype == "rtf":
                    filepath = default_storage.save('cv/temp.doc', f)
                email, contact, finalpath = uploadFile(filetype, filepath)
                obj = Profile()
                obj.email = email
                obj.contact = contact
                obj.cv = finalpath
                obj.save()
            messages.success(request, "Files uploaded successfully!")
        else:
            messages.error(request, "Unable to upload files.\\nTry again!")
    return redirect('/')

def uploadUsingFolderLocation(request):
    if request.method == 'POST':
        form = FolderUploadForm(request.POST)
        if form.is_valid():
            urlPath = form.cleaned_data['folder']
            check = re.match(r'^[a-zA-Z]:\\(((?![<>:"\/\\|?*]).)+((?<![ .])\\)?)*$', urlPath)
            if check:
                for i in os.listdir(urlPath):
                    if os.path.isfile(os.path.join(urlPath, i)) and str(i).split('.')[-1] in ['pdf', 'docx', 'doc', 'rtf']:
                        filetype = str(i).split('.')[-1]
                        if filetype == "pdf":
                            copyfile(os.path.join(urlPath, i), os.path.join(settings.MEDIA_ROOT, 'cv/temp.pdf'))
                            filepath = 'cv/temp.pdf'
                        elif filetype == "docx":
                            copyfile(os.path.join(urlPath, i), os.path.join(settings.MEDIA_ROOT, 'cv/temp.docx'))
                            filepath = 'cv/temp.docx'
                        elif filetype == "doc" or filetype == "rtf":
                            copyfile(os.path.join(urlPath, i), os.path.join(settings.MEDIA_ROOT, 'cv/temp.doc'))
                            filepath = 'cv/temp.doc'
                        email, contact, finalpath = uploadFile(filetype, filepath)
                        obj = Profile()
                        obj.email = email
                        obj.contact = contact
                        obj.cv = finalpath
                        obj.save()
                messages.success(request, "Files uploaded from the folder successfully!")
            else:
                messages.error(request, "Not a valid folder location.\\nTry again!")
        else:
            messages.error(request, "Unable to upload files from the given folder location.\\nTry again!")
        return redirect('/')

class Echo:
    def write(self, value):
        return value

def downloadFile(request):
    obj = Profile.objects.filter().order_by('email')
    dct = {}
    for i in obj:
        dct[i.email] = [i.contact, "http://127.0.0.1:8000/media/" + str(i.cv).replace('\\', '/')]
    rows = ([["EMAIL", "CONTACT NO.", "LOCATION"]])
    rows += ([key, value[0], value[1]] for key, value in dct.items())
    buffer = Echo()
    writer = csv.writer(buffer)
    return StreamingHttpResponse(
        (writer.writerow(row) for row in rows),
        content_type="text/csv",
        headers={'Content-Disposition': 'attachment; filename="CV_List_Download.csv"'},
    )