from django.contrib import admin
from iarbre_data.models import MVTTile, Tile, Lcz, Vulnerability


class MVTTileAdmin(admin.ModelAdmin):
    list_display = ("id",)
    search_fields = ("id",)
    ordering = ("-id",)


class TileAdmin(admin.ModelAdmin):
    list_display = ("id",)
    search_fields = ("id",)
    ordering = ("-id",)


class LczAdmin(admin.ModelAdmin):
    list_display = ("id",)
    search_fields = ("id",)
    ordering = ("-id",)


class VulnerabilityAdmin(admin.ModelAdmin):
    list_display = ("id",)
    search_fields = ("id",)
    ordering = ("-id",)


admin.site.register(MVTTile, MVTTileAdmin)
admin.site.register(Tile, TileAdmin)
admin.site.register(Lcz, LczAdmin)
admin.site.register(Vulnerability, VulnerabilityAdmin)
