from django.db import models

# Create your models here.
from django.db import models


class EncryptedDoc(models.Model):
    wallet_address = models.CharField(max_length=255)
    doc_id = models.CharField(max_length=255)
    doc_meta = models.BinaryField()

    def __str__(self):
        return self.doc_meta
