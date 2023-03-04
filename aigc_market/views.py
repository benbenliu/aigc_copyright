from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse, HttpRequest
from cryptography.fernet import Fernet
from .models import EncryptedDoc
from uuid import uuid4
import json


def index(request: HttpRequest):
    return HttpResponse("Hello, world. You're at the aigc market index.")


def upload_page(request: HttpRequest):
    return render(request, 'upload_page.html')


def register_aigc(request: HttpRequest):
    # Get the parameters from the request
    wallet_address = request.POST.get('wallet_address')
    model_name = request.POST.get('model_name')
    model_version = request.POST.get('model_version')
    prompts = request.POST.get('prompts')
    media = request.FILES.get("media_file", None)
    if media:
        print(media.name)
    print(wallet_address, model_name, model_version, prompts)
    doc_id = str(uuid4())
    # Generate a random encryption key
    key = Fernet.generate_key()

    # Create a Fernet object with the encryption key
    fernet = Fernet(key)

    # Encrypt the prompts
    doc_meta_str = json.dumps({
        'model': model_name,
        'model_version': model_version,
        'prompts': prompts
    })
    doc_meta: bytes = fernet.encrypt(doc_meta_str.encode())
    # Store the request information in the database
    encrypted_doc_meta = EncryptedDoc.objects.create(
        wallet_address=wallet_address,
        doc_id=doc_id,
        doc_meta=doc_meta
    )
    encrypted_doc_meta.save()
    # Return the encryption key and the encrypted prompts to the front-end
    response = {
        'key': key.decode(),
        'doc_meta': doc_meta.decode()
    }
    print(response)
    return JsonResponse(response)
