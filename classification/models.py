from django.db import models
from django.contrib.postgres.fields import ArrayField

#Customize the model by custom manager
class ClassificationManager(models.Manager):
    #Create the classification subject
    def create_classification(self, classification_id, annotation, workflow_id, user_id, subject_id, \
     event_time, gravityspy_id, ifo, main_channel_name, event_generator, annotation_channel_names, hveto_round_number):
        self.classification_id=classification_id
        self.annotation=annotation
        self.workflow_id=workflow_id
        self.user_id=user_id
        self.subject_id=subject_id
        self.event_time=event_time
        self.gravityspy_id=gravityspy_id
        self.ifo=ifo
        self.main_channel_name=main_channel_name
        self.event_generator=event_generator
        self.annotation_channel_names=annotation_channel_names
        self.hveto_round_number=hveto_round_number
        classification_subject=self.get_or_create(classification_id=self.classification_id, annotation=self.annotation, workflow_id=self.workflow_id, user_id=self.user_id, \
         subject_id=self.subject_id, event_time=self.event_time, gravityspy_id=self.gravityspy_id, ifo=self.ifo, main_channel_name=self.main_channel_name, \
         event_generator=self.event_generator, annotation_channel_names=self.annotation_channel_names, hveto_round_number=self.hveto_round_number)
        return classification_subject

#Create the Django model
class Classification(models.Model):
    """The frame work for a single Gravity Spy annotation/classification from a volunteer
    id is 420780262
    annotation is [{'task': 'T0', 'value': [{'x': 401.2159729003906, 'y': 1486.4444580078125, 'tool': 0, 'frame': 0, 'details': []}]}]
    workflow is 21793
    user is 386563
    subject is 76084855    
    """
    #Field defining
    classification_id = models.IntegerField()
    annotation = ArrayField(models.IntegerField())
    workflow_id = models.IntegerField()
    user_id = models.IntegerField()
    subject_id = models.IntegerField()

    event_time = models.FloatField()
    gravityspy_id = models.CharField(max_length=30)
    ifo = models.CharField(max_length=2)
    main_channel_name = models.CharField(max_length=100)
    event_generator = models.CharField(max_length=100)
    annotation_channel_names = ArrayField(models.CharField(max_length=100))
    hveto_round_number = models.IntegerField()
    ## TODO: project_id?

    #Add a method on custom manager
    objects = ClassificationManager()

