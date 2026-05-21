from django.db import models
from django.utils.timezone import now

optional = {
    'null': True,
    'blank': True
}

# Create your models here. 
class AuditLog(models.Model):
    
    AUDIT_TYPE = (
        (0, ''),
        (1, 'Initial Registration')
    )
    EVENT = (
        (0, 'New'),
        (1, 'Update'),
        (1, 'Delete')
    )

    STATUS = (
        (0, 'Pending'),
        (1, 'Approve'),
        (-1, 'Rejected'),
        (2, 'Draft')
    )

    audit_type = models.IntegerField(choices=AUDIT_TYPE, default=0)
    status = models.IntegerField(choices=STATUS, default=0)
    event = models.IntegerField(choices=EVENT, default=0)
    search = models.CharField(max_length=200, default='', **optional)
    current_details = models.TextField(default='', **optional)
    remarks = models.TextField(default='', **optional)
    new_details = models.TextField(default='', **optional)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, default=None, **optional)
    date_updated = models.DateTimeField(**optional)
    date_created = models.DateTimeField(default=now)
    
    