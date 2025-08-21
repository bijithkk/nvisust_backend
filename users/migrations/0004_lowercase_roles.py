from django.db import migrations, models


def lowercase_roles(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    User = apps.get_model('users', 'User')

    mapping = {
        'ADMIN': 'admin',
        'MANAGER': 'manager',
        'EMPLOYEE': 'employee',
    }

    # Ensure lowercase roles exist and reassign users from uppercase to lowercase
    for upper_name, lower_name in mapping.items():
        lower_role, _ = Role.objects.get_or_create(name=lower_name)
        # Move users pointing to the uppercase role to the lowercase role
        for user in User.objects.filter(role__name=upper_name):
            user.role = lower_role
            user.save(update_fields=['role'])
        # Remove any lingering uppercase role rows
        Role.objects.filter(name=upper_name).delete()


def uppercase_roles(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    User = apps.get_model('users', 'User')

    mapping = {
        'admin': 'ADMIN',
        'manager': 'MANAGER',
        'employee': 'EMPLOYEE',
    }

    for lower_name, upper_name in mapping.items():
        upper_role, _ = Role.objects.get_or_create(name=upper_name)
        for user in User.objects.filter(role__name=lower_name):
            user.role = upper_role
            user.save(update_fields=['role'])
        Role.objects.filter(name=lower_name).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0003_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(
                choices=[('admin', 'Admin'), ('manager', 'Manager'), ('employee', 'Employee')],
                max_length=20,
                unique=True,
            ),
        ),
        migrations.RunPython(lowercase_roles, uppercase_roles),
    ]


