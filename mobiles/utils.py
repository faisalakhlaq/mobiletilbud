from .models import MobileBrand as new_brand
from core.models import MobileBrand as core_brand

def bulk_copy_table_data():
    queryset = core_mobile.objects.all().values('name', 'full_name', 'brand', 'cash_price', 'slug')
    # new_objects = [new_mobile(**values) for values in queryset]
    # new_mobile.objects.bulk_create(new_objects)
    for values in queryset:
        brand = MobileBrand.objects.get(id=values['brand'])
        values['brand'] = brand
        new_mobile.objects.create(**values)

def bulk_copy_brand_data():
    queryset = core_brand.objects.all().values()
    new_objects = [new_brand(**values) for values in queryset]
    new_brand.objects.bulk_create(new_objects)
