from myapp.models import Point, Visit, Round, Guard


def create_visit(guard: Guard, round: Round, point: Point):
    return Visit.objects.create(guard=guard, round=round, point=point)


def get_visit(round: Round, point: Point):
    return Visit.objects.filter(round=round, point=point).order_by('-created_at').first()
