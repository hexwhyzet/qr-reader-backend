from myapp.models import Point, Visit, Round


def create_visit(round: Round, point: Point):
    return Visit.objects.create(round=round, point=point)
