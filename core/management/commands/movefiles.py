from django.core.management.base import BaseCommand, CommandError
from core.models import DataFileInfo, ProfileInfo, ProfileCreationRun
from django.core.files import File

import os

class Command(BaseCommand):
    help = 'Performs data processing'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        datafiles = [df for df in DataFileInfo.objects.all()]
        runs = [run for run in ProfileCreationRun.objects.all()]

        for df in datafiles:
            with open(os.path.join('media', df.data.name), 'rb') as f:
                ff = File(f)
                dup = DataFileInfo(data = ff, \
                    device = df.device, \
                    start_date = df.start_date, \
                    file_type = df.file_type)
                dup.save()
            df.delete()
                
        for r in runs:
            dup = None
            with open(os.path.join('media', r.parsed_event_files.name), 'rb') as fp:
                with open(os.path.join('media', r.unlock_data.name), 'rb') as fu:
                    with open(os.path.join('media', r.checkpoint_data.name), 'rb') as fc:
                        ffp = File(fp)
                        ffu = File(fu)
                        ffc = File(fc)
                        dup = DataFileInfo(parsed_event_files = ffp, \
                            unlock_data = ffu, \
                            checkpoint_data = ffc, \
                            run_date = r.run_date)
                        dup.save()

            for p in r.profileinfo_set:
                with open(os.path.join('media', p.profile_file.name), 'rb') as f:
                    ff = File(f)
                    pdup = ProfileInfo(device = p.device, \
                        run = dup, \
                        profile_file = ff, \
                        profile_type = p.profile_type, \
                        used_class_samples = p.used_class_samples, \
                        score = p.score, \
                        precision = p.precision, \
                        recall = p.recall, \
                        fscore = p.fscore, \
                        description = p.description)
                    pdup.save()
                p.delete()

            r.delete()