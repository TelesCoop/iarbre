import factory
from django.contrib.gis.geos import Polygon
from iarbre_data.models import Tile, Iris, City, TileFactor


class IrisFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Iris

    geometry = factory.LazyFunction(lambda: Polygon.from_bbox((0, 0, 1, 1)))
    code = factory.Faker("random_int", min=69123, max=69999)
    name = factory.Faker("name")


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City

    geometry = factory.LazyFunction(lambda: Polygon.from_bbox((0, 0, 1, 1)))
    code = factory.Faker("random_int", min=69123, max=69999)
    name = factory.Faker("name")
    tiles_generated = True
    tiles_computed = True


class TileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tile

    geometry = factory.LazyFunction(lambda: Polygon.from_bbox((0, 0, 1, 1)))
    plantability_indice = factory.Faker("pyfloat", min_value=-5, max_value=15)
    plantability_normalized_indice = factory.Faker("pyfloat", min_value=0, max_value=1)
    iris = factory.SubFactory(IrisFactory)
    city = factory.SubFactory(CityFactory)


class TileFactorsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TileFactor

    tile = factory.SubFactory(TileFactory)
    factor = factory.Faker("name")
    value = factory.Faker("pyfloat", min_value=0, max_value=1)
