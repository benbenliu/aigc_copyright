# Create your models here.
from django.db import models


class EncryptedDoc(models.Model):
    wallet_address = models.CharField(max_length=255)
    ts = models.DateTimeField()
    doc_id = models.CharField(max_length=255)
    encrypted_doc = models.BinaryField()
    encryption_key = models.BinaryField()
    metadata_uri = models.CharField(max_length=255)
    media_uri = models.CharField(max_length=255)
    tx_hash = models.CharField(max_length=255, null=True)
    network = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.doc_id
