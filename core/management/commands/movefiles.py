from django.core.management.base import BaseCommand, CommandError
from core.models import DataFileInfo, ProfileInfo, ProfileCreationRun
from django.core.files import File

class Command(BaseCommand):
    help = 'Performs data processing'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        datafiles = DataFileInfo.objects.all()
        runs = ProfileCreationRun.objects.all()

        for df in datafiles:
            with open(df.data.path, 'rb') as f:
                ff = File(f)
                dup = DataFileInfo(data = ff, \
                    device = df.device, \
                    start_date = df.start_date, \
                    file_type = df.file_type)
                dup.save()
            df.delete()
                
        for r in runs:
            dup = None
            with open(r.parsed_event_files.path, 'rb') as fp:
                with open(r.unlock_data.path, 'rb') as fu:
                    with open(r.checkpoint_data.path, 'rb') as fc:
                        ffp = File(fp)
                        ffu = File(fu)
                        ffc = File(fc)
                        dup = DataFileInfo(parsed_event_files = ffp, \
                            unlock_data = ffu, \
                            checkpoint_data = ffc, \
                            run_date = r.run_date)
                        dup.save()

            for p in r.profileinfo_set:
                with open(p.profile_file.path, 'rb') as f:
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