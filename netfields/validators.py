from django.core.exceptions import ValidationError


def validate_ipnetwork(value):
    """
    Validate IPNetwork to ensure there are no bits to the right of the mask
    """
    if value and value.ip != value.network:
        raise ValidationError(u'Network "%s" has bits set to right of mask' % value)
