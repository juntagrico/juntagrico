from django.db import migrations


def move_is_extra(apps, schema_editor):
    types = apps.get_model('juntagrico', 'SubscriptionType')
    for type in types.objects.all():
        type.is_extra = type.bundle.product.is_extra
        type.save()


def copy_category(apps, schema_editor):
    products = apps.get_model('juntagrico', 'SubscriptionProduct')
    categories = apps.get_model('juntagrico', 'SubscriptionCategory')
    replacements = {}
    for product in products.objects.all():
        replacements[product] = categories.objects.create(name=product.name, description=product.description)
    bundles = apps.get_model('juntagrico', 'SubscriptionBundle')
    for bundle in bundles.objects.filter(visible=True):
        bundle.category = replacements[bundle.product]
        bundle.save()


def initialize_products(apps, schema_editor):
    bundles = apps.get_model('juntagrico', 'SubscriptionBundle')
    product_size = apps.get_model('juntagrico', 'ProductSize')
    for bundle in bundles.objects.filter(depot_list=True):
        product_size.objects.create(name=bundle.name, units=bundle.units, bundle=bundle, product=bundle.product)


class Migration(migrations.Migration):

    dependencies = [
        ('juntagrico', '0046_pre_743'),
    ]

    operations = [
        migrations.RunPython(move_is_extra),
        migrations.RunPython(copy_category),
        migrations.RunPython(initialize_products),
    ]
