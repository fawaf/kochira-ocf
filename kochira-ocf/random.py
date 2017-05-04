"""
Random
"""

from kochira.service import Service
import random

service = Service(__name__, __doc__)

@service.command(r"!rand(om)? (?P<num>.*)$")
def get_subnet(ctx, num):
    """
    Generate random number
    """
    try:
        ctx.message(str(random.randint(0, int(num))))
    except ValueError as e:
        ctx.message("wat: {0}".format(e))
