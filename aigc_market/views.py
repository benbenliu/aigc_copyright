from django.shortcuts import render

# Create your views here.
from django.http import HttpRequest
import cryptography
from cryptography.fernet import Fernet
from .models import EncryptedDoc
from uuid import uuid4
import json
from aigc_market.utils.web3_utils import DavinciMindMasterContract
import datetime


def index(request: HttpRequest):
    return render(request, 'index.html')


def upload_page(request: HttpRequest):
    return render(request, 'upload_page.html')


def marketplace(request: HttpRequest):
    return render(request, 'market.html')


def my_creations(request: HttpRequest):
    # hardcode for now
    my_docs = EncryptedDoc.objects.all()
    return render(request, 'registered_doc.html', context={'docs': my_docs})


def register_aigc(request: HttpRequest):
    # Get the parameters from the request
    wallet_address = request.POST.get('wallet_address')
    model_name = request.POST.get('model_name')
    model_version = request.POST.get('model_version')
    prompts = request.POST.get('prompts')
    media = request.FILES.get("media_file")
    media_content = media.read() if media is not None else b''
    doc_id = str(uuid4())
    # Generate a random encryption key
    key = Fernet.generate_key()

    # Create a Fernet object with the encryption key
    fernet = Fernet(key)

    # Encrypt the prompts
    doc_str = json.dumps({
        'model': model_name,
        'model_version': model_version,
        'prompts': prompts
    })
    encrypted_doc: bytes = fernet.encrypt(doc_str.encode())
    # Return the encryption key and the encrypted prompts to the front-end
    master_contract = DavinciMindMasterContract()
    encryptor_spec = {
        'lib': 'cryptography.fernet',
        'version': cryptography.__version__
    }
    creation_results = master_contract.mint_aigc_nft(
        wallet_address, doc_id, key, encrypted_doc, encryptor=json.dumps(encryptor_spec),
        media_content=media_content)
    creation_results.update(
        {
            'encryption_key': key.decode()
        }
    )
    # Store the request information in the database
    encrypted_doc_meta = EncryptedDoc.objects.create(
        wallet_address=wallet_address,
        ts=datetime.datetime.utcnow(),
        doc_id=doc_id,
        encrypted_doc=encrypted_doc,
        encryption_key=key,
        metadata_uri=creation_results['nft_metadata_uri'],
        media_uri=creation_results['media_uri'],
        tx_hash=creation_results['tx_hash'],
        network=creation_results['network']
    )
    encrypted_doc_meta.save()
    return render(request, 'registered_doc.html', context={'docs': [encrypted_doc_meta]})
