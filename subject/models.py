# -*- coding: utf-8 -*-
# Copyright (C) Scott Coughlin (2017-)
#
# This file is part of gravityspy.
#
# gravityspy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gravityspy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gravityspy.  If not, see <http://www.gnu.org/licenses/>.

from gravityspy_ligo.utils import utils, hveto_parser
from gravityspy_ligo.table.events import id_generator
from gwpy import time
from PIL import Image
from itertools import groupby
from django.db import models
from django.contrib.postgres.fields import ArrayField
import multiprocessing
import numpy
import os
import datetime
import panoptes_client
import glob

class GravitySpySubjectManager(models.Manager):
    def create_gravityspy_subject(self, event_time, ifo, config, gravityspy_id=None, event_generator=None, auxiliary_channel_correlation_algorithm=None, number_of_aux_channels_to_show=None, manual_list_of_auxiliary_channel_names=None):
        """Example of docstring on the __init__ method.
        Args:
            event_time (float): The GPS time at which an excess noise event occurred.
            ifo (str): What interferometer had this an excess noise event
            event_generator (str): The algorithm that tells us an excess noise event occurred
            auxiliary_channel_correlation_algorithm (str): The algorithm that tells us the names of the top X correlated auxiliary channels with respect to h(t).
            number_of_aux_channels_to_show (int): This number will determine the top N number of channels from the list provided by the auxiliary_channel_correlation_algorithm that will be kept and shown for this Subject.
            manual_list_of_auxiliary_channel_names (list): This will override any auxiliary channel list that might have been supplied by the auxiliary_channel_correlation_algorithm and force this to be the auxiliary channels that are associated with this Subject.
        """
        self.event_time = event_time
        if gravityspy_id is None:
            gravityspy_id = id_generator(event_time, size=20)
        self.gravityspy_id = gravityspy_id
        self.ifo = ifo
        self.main_channel = '{0}:GDS-CALIB_STRAIN'.format(ifo)
        self.event_generator = event_generator
        self.config = config
        self.all_channels = []
        self.frametypes = []
        self.q_values = []
        self.q_transforms = []
        self.ldvw_glitchdb_image_filenames = []
        self.zooniverse_subject_image_filenames = []
        self.zooniverse_subject_ids = []
        self.hveto_round_number = -1

        # If a manual list of auxiliary channels were provided, we can set a lot fo these attributes right now.
        if manual_list_of_auxiliary_channel_names is not None:
            # Check to make sure that channel names were supplied with names <ifo>:
            for channel in manual_list_of_auxiliary_channel_names:
                if '{0}:'.format(ifo) not in channel:
                    raise ValueError("Please supply aux channel name with leading `<ifo>:`")

            self.list_of_auxiliary_channel_names = manual_list_of_auxiliary_channel_names

            # no matter what was passed, override these to be None
            self.number_of_aux_channels_to_show = None
            self.auxiliary_channel_correlation_algorithm = None
        elif 'hveto' in auxiliary_channel_correlation_algorithm.keys():

            # if we passed 'hveto' as our algorithm, we must also have identified what round this glitch is associated with.
            round_number = auxiliary_channel_correlation_algorithm['hveto']
            self.hveto_round_number = round_number

            self.auxiliary_channel_correlation_algorithm = auxiliary_channel_correlation_algorithm
            self.number_of_aux_channels_to_show = number_of_aux_channels_to_show

            # based on the start and end time, produce a date timestamp with YYYYMMDD
            # convert start time from gps to regular date
            event_time_in_date_format = time.from_gps(self.event_time)

            event_time_in_YYYYMMDD_format = event_time_in_date_format.strftime("%Y%m%d")

            each_rounds_svg_file = glob.glob("/home/detchar/public_html/hveto/day/{0}/latest/plots/*ROUND_{1}*.svg".format(event_time_in_YYYYMMDD_format, round_number))

            for each_round_svg in each_rounds_svg_file:
                auxiliary_channels_ordered_by_signifigance = hveto_parser.hveto_parser(each_round_svg)

            self.list_of_auxiliary_channel_names = auxiliary_channels_ordered_by_signifigance[0:number_of_aux_channels_to_show]
        else:
            raise ValueError("You supplied a auxiliary_channel_correlation_algorithm that is not recognized")

        # create the final list of all channels and frametypes associated with this subject
        # Append main channel name and frametype
        self.all_channels.append(self.main_channel)
        self.frametypes.append('{0}_HOFT_C00'.format(ifo))
        # Append aux channel names and frametype
        for aux_channel in self.list_of_auxiliary_channel_names:
            self.frametypes.append('{0}_R'.format(ifo))
        self.all_channels.extend(self.list_of_auxiliary_channel_names)

        gravityspy_plus_subject = self.create(event_time=self.event_time, gravityspy_id=self.gravityspy_id, ifo=self.ifo, main_channel=self.main_channel, event_generator=str(self.event_generator), q_values=self.q_values, list_of_auxiliary_channel_names=self.list_of_auxiliary_channel_names, zooniverse_subject_ids=self.zooniverse_subject_ids, hveto_round_number=self.hveto_round_number)

        # do something with the book
        return gravityspy_plus_subject

    def make_omega_scans(self, pool=None, **kwargs):
        # Parse key word arguments
        verbose = kwargs.pop('verbose', False)
        nproc = kwargs.pop('nproc', 1)

        inputs = ((self.event_time, self.config, channel_name, frametype, verbose)
                  for channel_name, frametype, in zip(self.all_channels, self.frametypes))

        # make q_scans
        if (pool is None) and (nproc > 1):
            with multiprocessing.Pool(nproc) as pool:
                output = pool.map(utils._make_single_qscan,
                               inputs)
        elif (pool is None) and (nproc == 1):
            output = list(map(utils._make_single_qscan, inputs))
        elif pool is not None:
            output = pool.map(utils._make_single_qscan,
                              inputs)

        # raise exceptions (from multiprocessing, single process raises inline)
        for event_time, q_transform, q_value in output:
            self.q_values.append(q_value)
            self.q_transforms.append(q_transform)
       
        box_x =  self.q_transforms[0].xindex
        box_y =  self.q_transforms[0].yindex
        box_x_dur =  self.q_transforms[0].dx
        box_y_dur =  self.q_transforms[0].dy
        for q_scan in self.q_transforms:
            setattr(q_scan, 'box_x', box_x)
            setattr(q_scan, 'box_y', box_y)
            setattr(q_scan, 'box_x_dur', box_x_dur)
            setattr(q_scan, 'box_y_dur', box_y_dur)

    def save_omega_scans(self, pool=None, **kwargs):
        # Parse key word arguments
        plot_directory = kwargs.pop('plot_directory', os.path.join(os.getcwd(), 'plots', time.from_gps(self.event_time).strftime('%Y-%m-%d'), str(self.event_time)))
        verbose = kwargs.pop('verbose', False)
        nproc = kwargs.pop('nproc', 1)

        inputs = inputs = ((self.event_time, self.ifo, '{0}_{1}'.format(self.gravityspy_id, channel_name), self.config, plot_directory, channel_name, frametype, verbose, q_transform) for channel_name, frametype, q_transform in zip(self.all_channels, self.frametypes, self.q_transforms))

        # make q_scans
        if (pool is None) and (nproc > 1):
            with multiprocessing.Pool(nproc) as pool:
                output = pool.map(utils._save_q_scans,
                               inputs)
        elif (pool is None) and (nproc == 1):
            output = list(map(utils._save_q_scans, inputs))
        elif pool is not None:
            output = pool.map(utils._save_q_scans,
                              inputs)

        for event_time, individual_image_filenames, combined_image_filename in output:
            self.ldvw_glitchdb_image_filenames.append(combined_image_filename)
            self.zooniverse_subject_image_filenames.extend(individual_image_filenames)

    def combine_images_for_subject_upload(self, number_of_rows=1, **kwargs):
        plot_directory = kwargs.pop('plot_directory', os.path.join(os.getcwd(), 'plots', time.from_gps(self.event_time).strftime('%Y-%m-%d'), str(self.event_time)))

        # group the images by their durations
        f = lambda x: x.split('_')[-1]
        images_grouped_by_duration = [list(g) for k, g in groupby(sorted(self.zooniverse_subject_image_filenames, key=f), key=f)]

        def group_non_main_channels(lst, n):
            return zip(*[iter(lst)]*n)

        all_images_to_combine = {}
        for images_with_a_given_duration in images_grouped_by_duration:
             main_channel_file = [x for x in images_with_a_given_duration if self.main_channel in x]
             non_main_channel_files = [x for x in images_with_a_given_duration if self.main_channel not in x]
             non_main_channel_files_in_chunks = list(group_non_main_channels(non_main_channel_files, number_of_rows))
             number_of_grouping = len(non_main_channel_files_in_chunks)
             main_channel_file = [main_channel_file]*number_of_grouping
             for idx, main_channel in enumerate(main_channel_file):
                 if "subject_part_{0}".format(idx+1) not in all_images_to_combine.keys():
                     all_images_to_combine["subject_part_{0}".format(idx+1)] = [] 
                 main_channel_copy = main_channel.copy()
                 main_channel_copy.extend(non_main_channel_files_in_chunks[idx])
                 all_images_to_combine["subject_part_{0}".format(idx+1)].append(main_channel_copy)

        self.zooniverse_subject_image_filenames = {}
        for subject_part, all_image_files_for_this_part in all_images_to_combine.items():
            if subject_part not in self.zooniverse_subject_image_filenames.keys():
                 self.zooniverse_subject_image_filenames[subject_part] = {}
                 self.zooniverse_subject_image_filenames[subject_part]['images_to_upload'] = []

            for images_to_combine in all_image_files_for_this_part:
                # creating a new image and pasting 
                # the images
                combined_image = Image.new("RGB", (800, 600 * (number_of_rows + 1)), "white")

                all_channels = []
                for image_idx, image_filename in enumerate(images_to_combine):
                    # channel_name
                    channel_name = image_filename.split('_', 2)[-1].split('_spectrogram')[0]
                    all_channels.append(channel_name)

                    # obtain duration from filename
                    duration = image_filename.split('_')[-1].replace('.png', '')

                    # opening up of images
                    sub_image = Image.open(image_filename)

                    # pasting the first image (image_name,
                    # (position))
                    combined_image.paste(sub_image, (0, 0 + 600*image_idx))

                combined_image_filename = os.path.join(plot_directory, '{0}_{1}_{2}.png'.format(self.ifo, subject_part, duration))
                combined_image.save(combined_image_filename)
                self.zooniverse_subject_image_filenames[subject_part]['images_to_upload'].extend([combined_image_filename])
                self.zooniverse_subject_image_filenames[subject_part]['channels_in_this_subject'] = all_channels

    def upload_to_zooniverse(self, subject_set_id, project='1104'):
        """Obtain omicron triggers to run gravityspy on

        Parameters:
            subject_set_id (optional, int) : subject set id to upload to

        Returns:
            `Events` table
        """
        for subject_part, subject_part_data in self.zooniverse_subject_image_filenames.items():
            images_for_subject_part = sorted(subject_part_data['images_to_upload'], reverse=True)
            subject = panoptes_client.Subject()
            subject.links.project = project
            subject.metadata['date'] = time.from_gps(self.event_time).strftime("%Y%m%d")
            print('subject event_time: ',self.event_time)
            subject.metadata['subject_id'] = str(self.gravityspy_id)
            print('subject_id: ',str(self.gravityspy_id))
            aux_channel_str = self.list_of_auxiliary_channel_names[0][3:] #lst to str
            new_url = "https://gswiki.ischool.syr.edu/find/Channels/{}".format(aux_channel_str)
            subject.metadata['aux_url'] = str(new_url)

            for idx, channel_name in enumerate(subject_part_data['channels_in_this_subject']):
                subject.metadata['channel_name_{0}'.format(idx+1)] = channel_name
                
            for idx, channel_name in enumerate(subject_part_data['channels_in_this_subject']):
                if ':' in channel_name: #clean the channel names in 'channels_in_this_subject'
                    channel_name_parts = channel_name.split('/') #split every '/'
                    channel_prefix = channel_name_parts[6][:2] #prefix = ifo
                    channel_suffix = channel_name_parts[6].split(':', 1)[1] #suffix = channel name
                    channel_name = "{}:{}".format(channel_prefix, channel_suffix) #desired new channel name
                    subject.metadata['channel_name_{0}'.format(idx+1)] = channel_name
                    print('channel_name: ',channel_name)
                else:
                    subject.metadata['channel_name_{0}'.format(idx+1)] = channel_name
                
            for idx, image in enumerate(images_for_subject_part):
                subject.add_location(str(image))
                subject.metadata['Filename{0}'.format(idx+1)] = image.split('/')[-1]
            subject.save()
            self.zooniverse_subject_ids.append(int(subject.id))
            for idx, image in enumerate(images_for_subject_part):
                setattr(self, 'url{0}'.format(idx), subject.raw['locations'][idx]['image/png'].split('?')[0])

            subjectset = panoptes_client.SubjectSet.find(subject_set_id)
            subjectset.add(subject)

class GravitySpySubject(models.Model):
    """The frame work for thinking about a single Gravity Spy subject
    """
    event_time = models.FloatField()
    gravityspy_id = models.CharField(max_length=30)
    ifo = models.CharField(max_length=2)
    main_channel = models.CharField(max_length=100)
    event_generator = models.CharField(max_length=100)
    q_values = ArrayField(models.FloatField())
    list_of_auxiliary_channel_names = ArrayField(models.CharField(max_length=100))
    zooniverse_subject_ids = ArrayField(models.IntegerField())
    hveto_round_number = models.IntegerField()

    objects = GravitySpySubjectManager()
