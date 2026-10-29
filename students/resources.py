from import_export.widgets import ForeignKeyWidget
from administrative.models import Department

class CreatingForeignKeyWidget(ForeignKeyWidget):
    """Create the related object if it does not exist."""
    def clean(self, value, row=None, **kwargs):
        if not value:
            return None
        obj, _created = self.model.objects.get_or_create(
            **{self.field: value}
        )
        return obj