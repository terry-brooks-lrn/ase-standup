# Generated by Django 4.2.6 on 2024-08-29 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agenda',
            name='date',
            field=models.CharField(default='2024-08-29', primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='section',
            field=models.CharField(choices=[('REVIEW', 'Ticket Help or Review'), ('MONITOR', 'Ticket Monitoring'), ('FOCUS', "Client's Need Focus or Attention"), ('CALLS', 'Upcoming Client Calls'), ('INTERNAL', 'Internal Tasks'), ('NEEDS', 'Team, Departmental, Organizational Needs'), ('UPDATES', 'Personal, Social Updates'), ('MISC', 'Miscellaneous'), ('DOCS', 'Documentation Review and Enhancement'), ('IFEAT', 'internal Feature Requests')], max_length=65535),
        ),
        migrations.AlterField(
            model_name='supportengineer',
            name='username',
            field=models.CharField(max_length=255),
        ),
        migrations.AddIndex(
            model_name='agenda',
            index=models.Index(fields=['date'], name='agendas_date_7addc9_idx'),
        ),
        migrations.AddIndex(
            model_name='agenda',
            index=models.Index(fields=['driver'], name='agendas_driver__680be4_idx'),
        ),
        migrations.AddIndex(
            model_name='agenda',
            index=models.Index(fields=['notetaker'], name='agendas_notetak_bcc76d_idx'),
        ),
        migrations.AddIndex(
            model_name='item',
            index=models.Index(fields=['date_created'], name='items_date_cr_753d2d_idx'),
        ),
        migrations.AddIndex(
            model_name='item',
            index=models.Index(fields=['date_created', 'section', 'status'], name='items_date_cr_69ea7e_idx'),
        ),
        migrations.AddIndex(
            model_name='item',
            index=models.Index(fields=['creator', 'section', 'status'], name='items_creator_da63da_idx'),
        ),
        migrations.AddIndex(
            model_name='item',
            index=models.Index(fields=['added_to_supportmail', 'added_to_supportmail_on'], name='items_added_t_003926_idx'),
        ),
        migrations.AddIndex(
            model_name='item',
            index=models.Index(fields=['last_modified', 'section', 'status'], name='items_last_mo_ae8bed_idx'),
        ),
        migrations.AddIndex(
            model_name='item',
            index=models.Index(fields=['last_modified', 'status'], name='items_last_mo_df1974_idx'),
        ),
        migrations.AddIndex(
            model_name='item',
            index=models.Index(fields=['last_modified'], name='items_last_mo_4acfb1_idx'),
        ),
    ]
