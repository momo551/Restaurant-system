from django.contrib import admin
from .models import Ingredient, Recipe, Supplier, PurchaseOrder, PurchaseOrderItem, StockMovement

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'unit', 'reorder_level', 'is_active', 'updated_at')
    search_fields = ('name',)
    list_filter = ('unit', 'is_active')

class RecipeInline(admin.TabularInline):
    model = Recipe
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'ingredient', 'quantity_required')
    search_fields = ('menu_item__name', 'ingredient__name')
    list_filter = ('menu_item__category',)

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ('name', 'phone')

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'status', 'user', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [PurchaseOrderItemInline]

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'quantity', 'type', 'user', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('ingredient__name', 'notes')
    readonly_fields = ('created_at',)

