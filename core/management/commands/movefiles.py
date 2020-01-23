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

        # for df in datafiles:
        #     with open(os.path.join('media', df.data.name), 'rb') as f:
        #         ff = File(f)
        #         df.data = ff
        #         df.save()
        #         print(f'datafile {df.id} replaced')
                
        for r in runs:
            if r.id != 1:
                with open(os.path.join('media', r.parsed_event_files.name), 'rb') as fp:
                    with open(os.path.join('media', r.unlock_data.name), 'rb') as fu:
                        with open(os.path.join('media', r.checkpoint_data.name), 'rb') as fc:
                            ffp = File(fp)
                            ffu = File(fu)
                            ffc = File(fc)
                            r.parsed_event_files = ffp
                            r.unlock_data = ffu
                            r.checkpoint_data = ffc
                            r.save()
                            print(f'run {r.id} replaced')

            for p in r.profileinfo_set.all():
                with open(os.path.join('media', p.profile_file.name), 'rb') as f:
                    ff = File(f)
                    p.profile_file = ff
                    p.save()
                    print(f'profile {p.id} replaced')