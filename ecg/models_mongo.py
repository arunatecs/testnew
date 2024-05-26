from djongo import models as mongo_models

class Ecg(mongo_models.Model):
    
    #data = mongo_models.TextField(max_length=1000)
    timestamp = mongo_models.DateTimeField(auto_now_add=True)
    #dateTime = mongo_models.DateField()
    _id = mongo_models.ObjectIdField(primary_key=True)
    value = mongo_models.JSONField()

   
    objects = mongo_models.DjongoManager()

    class Meta:
        _use_db = 'nonrel'
        #ordering = ("-timestamp", )

    #def __str__(self):
        #return self.timestamp 