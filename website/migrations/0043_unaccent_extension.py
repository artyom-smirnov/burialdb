from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension

class Migration(migrations.Migration):
    dependencies = [
        ('website', '0042_auto_20190303_1227'),
    ]
    
    operations = [
        UnaccentExtension()
    ]
