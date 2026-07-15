from django.contrib import admin
from .models import (
    ProjectInfo, FlatType, Amenity, Lead, SiteVisitor,
    PopupAd, Review, BuildingFlat, BrochureImage
)

admin.site.register(ProjectInfo)
admin.site.register(FlatType)
admin.site.register(Amenity)
admin.site.register(Lead)
admin.site.register(SiteVisitor)
admin.site.register(PopupAd)
admin.site.register(Review)
admin.site.register(BuildingFlat)
admin.site.register(BrochureImage)
