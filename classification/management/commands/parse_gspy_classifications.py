from __future__ import annotations
from cmath import e
from ctypes import sizeof
from django.core.management.base import BaseCommand, CommandError
import panoptes_client
import warnings

from classification.models import Classification
from subject.models import GravitySpySubject

class Command(BaseCommand):
    help = 'Querying the Gravity Spy Plus zooniverse project for classifications'
    def add_arguments(self, parser):
        parser.add_argument("--project-id", default='1104')
        parser.add_argument("--number-of-classifications", type=int, default=1000)
        parser.add_argument("--last-classification-id", type=int, default=None)
        parser.add_argument("--workflow-id", type=int, default=None)
        parser.add_argument("--user-id", type=int, default=None)
        parser.add_argument("--verbose", type=bool, default=True)

    def handle(self, *args, **options):
        warnings.warn('handle function is deprecated and will be removed soon.')
        kwargs_classifications = {"project_id" : options['project_id'],
                                  "scope" : 'project'}
        if options['last_classification_id'] is not None:
            kwargs_classifications["last_id"] = '{0}'.format(options['last_classification_id'])
            
        if options['workflow_id'] is not None:
            kwargs_classifications["workflow_id"] = '{0}'.format(options['workflow_id'])

        if options['user_id'] is not None:
            kwargs_classifications["user_id"] = '{0}'.format(options['user_id'])

        all_classifications = panoptes_client.Classification.where(**kwargs_classifications)

        list_of_classification_dictionaries = []
        
        # Loop until no more classifications
        for iN in range(0, options['number_of_classifications']):
            try:
                classification = all_classifications.next()
                list_of_classification_dictionaries.append(classification.raw)
            except:
                break

        for classification in list_of_classification_dictionaries:
            if classification['links']['workflow'] == kwargs_classifications["workflow_id"]:
                classification_id=classification['id']
                #Create an annotation dictionary
                annotation_counts = [0] * 3
                for i in range(0, 3):
                    annotation_counts[i] = 0
                #Get the annotations labels based on relative y coordinate
                annotation_list = classification['annotations'][0]['value']
                height = 600 #height of a spectrum in pixel
                for j in range(len(annotation_list)):
                    y = annotation_list[j]['y']
                    if y >= height and y < 2 * height:
                        annotation_counts[0] = 1
                    elif y >= 2 * height and y <= 3 * height:
                        annotation_counts[1] = 1
                    else:
                        annotation_counts[2] = 1

                workflow_id=classification['links']['workflow']
                user_id=classification['links']['user']
                subject_id=classification['links']['subjects'][0]      
                        
                # Query classification from subjects
                subject_entry = GravitySpySubject.objects.get(zooniverse_subject_ids__overlap=[int(subject_id)]) # TODO: Should be a more neat way for this
                event_time=subject_entry.event_time
                gravityspy_id=subject_entry.gravityspy_id
                ifo=subject_entry.ifo
                main_channel_name = subject_entry.main_channel
                event_generator=subject_entry.event_generator
                hveto_round_number=subject_entry.hveto_round_number

                #Save all the annotation labels in the list
                index = subject_entry.zooniverse_subject_ids.index(int(subject_id))
                annotation_channel_full_names = subject_entry.list_of_auxiliary_channel_names[index * 3:index * 3 + 3]
                annotation = []
                annotation_channel_names = []
                for k in range(len(annotation_counts)):
                    if annotation_counts[k] == 1:
                        annotation.append(k)
                        annotation_channel_names.append(annotation_channel_full_names[k])

                #Instantiate the classification object
                result_classification, saved = Classification.objects.create_classification(classification_id=classification_id, annotation=annotation, \
                 workflow_id=workflow_id,user_id = user_id, subject_id=subject_id, event_time=event_time, gravityspy_id=gravityspy_id, ifo=ifo, \
                 main_channel_name=main_channel_name, event_generator=event_generator, annotation_channel_names=annotation_channel_names, hveto_round_number=hveto_round_number)
                
                #Log on the terminal
                if options['verbose'] is True:
                    if saved is True:
                        # Classification is saved successfully
                        print("id is {0}".format(result_classification.classification_id))
                        print("annotation is {0}".format(result_classification.annotation))
                        print("workflow is {0}".format(result_classification.workflow_id))
                        print("user is {0}".format(result_classification.user_id))
                        print("subject is {0}".format(result_classification.subject_id))
                        print("main_channel_name is {0}".format(result_classification.main_channel_name))
                        print("annotation_channel_names are {0}".format(result_classification.annotation_channel_names))
                        # TODO: More information to print?

                    else:
                    # Classification is already existed in the table
                        print("classification with id {0} is existing".format(result_classification.classification_id))
