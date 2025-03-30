from django.db import models

class QRLog(models.Model):
    username = models.CharField(max_length=100)
    locker_id = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    qr_code = models.ImageField(upload_to="qrcodes/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.locker_id}"
