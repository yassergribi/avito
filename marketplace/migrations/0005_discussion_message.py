# Generated by Django 4.0.3 on 2023-07-03 20:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_alter_item_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discussion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='marketplace.profil')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='marketplace.profil')),
            ],
            options={
                'unique_together': {('receiver', 'sender')},
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('discussion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message', to='marketplace.discussion')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.profil')),
            ],
        ),
    ]