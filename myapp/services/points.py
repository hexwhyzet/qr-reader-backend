from myapp.models import Point


def get_point(point_id: int):
    return Point.objects.get(id=point_id)
