
#region Add Django Models To Exec Path

import os, sys

proj_path = os.environ.get('PYTHONPATH',None)

if not proj_path:
    raise RuntimeError('Must set PYTHONPATH to the root of your django project')

# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "opensource_staging.settings")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

#endregion

from invoke import task

from typing import *
import random,string

from django_bulk_update.helper import bulk_update

from django_simple_imports.simple_imports.model_importer import ModelImporter
from django_simple_imports.simple_imports.system_importer_v2 import SystemImporter
from django_simple_imports.tests_app.importers import ImageImporter,TagImporter,UserProfileImporter,\
    UserImporter,CompanyImporter

from django.contrib.auth.models import User
from django_simple_imports.tests_app.models import UserProfile,Company,Tag


@task()
def setup_import_examples(ctx):
    user = User.objects.create(
        username = 'foomanchu', email='foomanchu@gmail.com', first_name = 'Foo', last_name = 'manchu'
    )
    company = Company.objects.create(
        name = 'Foo Folk Tagging', natural_id = 'fft'
    )
    up = UserProfile.objects.create(
        user=user,
        company = company
    )
    print(f'Created {user.username} for company {company.name}.')
    return user,company,up


@task()
def test_importer(ctx, filepath):
    from django_simple_imports.tests_app.importers import UserImporter,UserProfileImporter,CompanyImporter,\
        TagImporter

    importers = [UserImporter(),UserProfileImporter(),CompanyImporter(),TagImporter()]

    #: Better than reading in a file, just manually add the necessary data to these importers, and check them out
    #: TODO: Need to re-think through the recursive properties of these guys.

    # # Knowing the ordering, we can test the importer managers directly,
    # with open(filepath,'r') as f:
    #     for line in f.readlines():
    #
    #         for i,v in line.split(','):
    #             importers[i]



@task()
def setup(ctx, outdir, updates = False):
    """
    Writes data to file for sample app to illustrate importer work.
    :param ctx:
    :param outdir:
    :param updates:
    :return:
    """
    user,company,up = setup_import_examples(ctx)
    if updates:
        #: Write some data to disk, and add a line to the outpath file with the same reference data data, but slightly
        #: modified image attribute data.
        pass

    #: Write foo data to file to be read in
    # username,company_natural_id,tag_name (o/slug) slug,path_of_image,image-name
    foo_image_path = '/home/ubuntu/site/uploads/images/'
    outpath = f'{outdir}/test_data.csv'
    tags: List[Tag] = []
    with open(outpath,'w+') as f:
        for i in range(20):
            tags.append(
                Tag(
                    company=company,
                    created_by=up,
                    rank=i,
                    slug=''.join(random.choices(population=string.ascii_uppercase+string.ascii_uppercase,k=4))
                )
            )
            slugs = f'{tags[0].slug}'

            for tag in tags[1:]:
                slugs = f'{slugs};{tag.slug}'

            f.write(f'{user.username},{company.natural_id},'
                    f'{slugs},{foo_image_path},foo_{i}.png\n')

    Tag.objects.bulk_create(tags)
    return outpath


@task()
def import_example_set(ctx, dirpath = ''):
    #: This is where the importers need to be given, and the importer invoked
    from django_simple_imports.simple_imports.model_importer import ModelImporter
    roll_back_import_example(ctx)

    if not dirpath:
        dirpath = os.getcwd()

    filepath = setup(ctx,outdir=dirpath)

    importers: List[ModelImporter] = [ImageImporter,TagImporter,UserProfileImporter,UserImporter,CompanyImporter]

    master_importer = SystemImporter(
        importers=importers,
        csvfilepath=filepath
    )

    master_importer.import_data()
    master_importer.get_new_objects()
    print('Done.')
    # #: TODO: Implement these getters
    # create_data = master_importer.get_creates()
    # update_data = master_importer.get_updates()
    #
    # Image.objects.bulk_create(create_data)
    #
    # #: Plugging in 3rd party update tool
    # bulk_update(update_data)


@task()
def roll_back_import_example(ctx):
    User.objects.all().delete()
    UserProfile.objects.all().delete()
    Company.objects.all().delete()
    Tag.objects.all().delete()
