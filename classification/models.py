from django.db import models
from django.contrib.postgres.fields import ArrayField

#Customize the model by custom manager
class ClassificationManager(models.Manager):
    #Create the classification subject
    def create_classification(self, classification_id, annotation, workflow_id, user_id, subject_id):
        self.classification_id=classification_id
        self.annotation=annotation
        self.workflow_id=workflow_id
        self.user_id=user_id
        self.subject_id=subject_id
        classification_subject = self.get_or_create(classification_id=self.classification_id, annotation=self.annotation, workflow_id=self.workflow_id, user_id=self.user_id, subject_id=self.subject_id)
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
    ##project_id?

    #Add a method on custom manager
    objects = ClassificationManager()

