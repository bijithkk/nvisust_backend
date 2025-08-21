from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_lowercase_roles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(
                max_length=150,
                help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                unique=False,
                verbose_name='username',
            ),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(verbose_name='email address', unique=True, max_length=254, null=True, blank=True),
        ),
    ]


