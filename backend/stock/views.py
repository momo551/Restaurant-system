from rest_framework import viewsets, status, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction, models
from decimal import Decimal
from .models import (
    Ingredient, Recipe, Supplier, PurchaseOrder, PurchaseOrderItem,
    StockMovement, LowStockAlert, WasteLog
)
from .serializers import (
    IngredientSerializer, RecipeSerializer, SupplierSerializer,
    PurchaseOrderSerializer, PurchaseOrderItemSerializer, StockMovementSerializer,
    LowStockAlertSerializer, WasteLogSerializer
)
from users.permissions import HasStockAccess, IsInventoryManager
from users.utils import LoggingMixin

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class IngredientViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [HasStockAccess]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['quantity', 'name']

    @action(detail=True, methods=['post'], permission_classes=[IsInventoryManager])
    def adjust_stock(self, request, pk=None):
        ingredient = self.get_object()
        quantity = request.data.get('quantity')
        type = request.data.get('type') # IN, OUT, ADJUSTMENT
        notes = request.data.get('notes', 'Manual adjustment')
        
        if quantity is None or type not in StockMovement.MovementType.values:
            return Response({'error': 'Quantity and valid movement type are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            quantity = Decimal(str(quantity))
            
            with transaction.atomic():
                if type == StockMovement.MovementType.IN:
                    ingredient.quantity += quantity
                elif type == StockMovement.MovementType.OUT:
                    if ingredient.quantity < quantity:
                        return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
                    ingredient.quantity -= quantity
                elif type == StockMovement.MovementType.ADJUSTMENT:
                    ingredient.quantity = quantity
                
                ingredient.save()
                
                StockMovement.objects.create(
                    ingredient=ingredient,
                    quantity=quantity if type != StockMovement.MovementType.ADJUSTMENT else ingredient.quantity,
                    type=type,
                    user=request.user,
                    notes=notes
                )
            
            return Response(IngredientSerializer(ingredient).data)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[HasStockAccess])
    def export_pdf(self, request):
        from django.http import HttpResponse
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import arabic_reshaper
        from bidi.algorithm import get_display
        import io
        import os

        # Font setup (Arabic support)
        font_path = r'C:\Windows\Fonts\arial.ttf'
        font_name = 'Arial-Arabic'
        pdfmetrics.registerFont(TTFont(font_name, font_path))

        def process_arabic(text):
            if not text: return ""
            reshaped_text = arabic_reshaper.reshape(str(text))
            bidi_text = get_display(reshaped_text)
            return bidi_text

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'ArabicTitle',
            parent=styles['Title'],
            fontName=font_name,
            fontSize=24,
            alignment=1, # Center
            spaceAfter=20
        )

        # Title
        elements.append(Paragraph(process_arabic("تقرير حالة المخزون"), title_style))
        elements.append(Spacer(1, 12))

        # Table Header
        data = [[
            process_arabic("الحالة"),
            process_arabic("الوحدة"),
            process_arabic("المتاح"),
            process_arabic("المكون")
        ]]
        
        ingredients = Ingredient.objects.all().order_by('name')
        for ing in ingredients:
            status_text = process_arabic("نقص في المخزون" if ing.quantity <= ing.reorder_level else "متوفر")
            data.append([
                status_text,
                process_arabic(ing.unit),
                process_arabic(str(float(ing.quantity))),
                process_arabic(ing.name)
            ])

        # Create Table
        table = Table(data, colWidths=[100, 80, 100, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="inventory_report.pdf"'
        response.write(buffer.getvalue())
        return response


class RecipeViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('menu_item', 'ingredient').all()
    serializer_class = RecipeSerializer
    permission_classes = [HasStockAccess]

    @action(detail=False, methods=['post'], permission_classes=[IsInventoryManager])
    def update_recipe(self, request):
        menu_item_id = request.data.get('menu_item')
        ingredients_data = request.data.get('ingredients', [])
        
        if not menu_item_id:
            return Response({'error': 'Menu item ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            from menu.models import MenuItem
            menu_item = MenuItem.objects.get(id=menu_item_id)
            
            with transaction.atomic():
                # Get IDs of ingredients in the new list to keep
                new_ingredient_ids = [item.get('ingredient') for item in ingredients_data if item.get('ingredient')]
                
                # Remove ingredients not in the new list
                Recipe.objects.filter(menu_item=menu_item).exclude(ingredient_id__in=new_ingredient_ids).delete()
                
                # Update or create
                for item in ingredients_data:
                    ing_id = item.get('ingredient')
                    qty = item.get('quantity_required')
                    
                    if ing_id and qty:
                        Recipe.objects.update_or_create(
                            menu_item=menu_item,
                            ingredient_id=ing_id,
                            defaults={'quantity_required': Decimal(str(qty))}
                        )
                        
            return Response({'status': 'Recipe updated successfully'})
        except MenuItem.DoesNotExist:
            return Response({'error': 'Menu item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def grouped_by_menu_item(self, request):
        from menu.models import MenuItem
        
        # Optimized with prefetch_related for recipes and their ingredients
        items = MenuItem.objects.filter(recipes__isnull=False).distinct().prefetch_related(
            models.Prefetch('recipes', queryset=Recipe.objects.select_related('ingredient'))
        )
        
        data = []
        for item in items:
            recipes = item.recipes.all()
            total_cost = sum(
                (r.quantity_required * (r.ingredient.last_purchase_price or Decimal('0')))
                for r in recipes
            )
            
            data.append({
                'id': item.id,
                'menu_item': item.id,
                'menu_item_name': item.name,
                'total_cost': float(total_cost),
                'ingredients': RecipeSerializer(recipes, many=True).data
            })
            
        return Response(data)

class SupplierViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsInventoryManager]
    search_fields = ['name', 'phone']

class PurchaseOrderViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all().order_by('-created_at')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsInventoryManager]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        po = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in PurchaseOrder.Status.values:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            
        if po.status == PurchaseOrder.Status.RECEIVED:
            return Response({'error': 'Cannot change status of a received order'}, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            po.status = new_status
            po.save()
            
            if new_status == PurchaseOrder.Status.RECEIVED:
                for item in po.items.all():
                    # Increase stock
                    item.ingredient.quantity += item.quantity
                    if item.price:
                        item.ingredient.last_purchase_price = item.price
                    item.ingredient.save()
                    
                    # Log movement
                    StockMovement.objects.create(
                        ingredient=item.ingredient,
                        quantity=item.quantity,
                        type=StockMovement.MovementType.IN,
                        user=request.user,
                        notes=f"Received PO #{po.id}"
                    )
                    
        return Response(PurchaseOrderSerializer(po).data)

class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.all().order_by('-created_at')
    serializer_class = StockMovementSerializer
    permission_classes = [HasStockAccess]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {
        'ingredient': ['exact'],
        'type': ['exact'],
        'user': ['exact'],
        'created_at': ['gte', 'lte'],
    }
    ordering_fields = ['created_at', 'quantity']


class LowStockAlertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LowStockAlert.objects.filter(is_resolved=False).order_by('-created_at')
    serializer_class = LowStockAlertSerializer
    permission_classes = [HasStockAccess]
    
    @action(detail=True, methods=['post'], permission_classes=[IsInventoryManager])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.is_resolved = True
        from django.utils import timezone
        alert.resolved_at = timezone.now()
        alert.save()
        return Response({'status': 'Alert resolved'})


class WasteLogViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = WasteLog.objects.all().order_by('-created_at')
    serializer_class = WasteLogSerializer
    permission_classes = [IsInventoryManager]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {
        'ingredient': ['exact'],
        'reason': ['exact'],
        'recorded_by': ['exact'],
        'created_at': ['gte', 'lte'],
    }
    ordering_fields = ['created_at', 'quantity']

    def perform_create(self, serializer):
        ingredient = serializer.validated_data['ingredient']
        quantity = serializer.validated_data['quantity']
        cost_at_time = ingredient.last_purchase_price

        with transaction.atomic():
            # Deduct from stock
            if ingredient.quantity < quantity:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("كمية الهالك أكبر من المخزون المتاح")
                
            ingredient.quantity -= quantity
            ingredient.save()

            # Record system movement
            StockMovement.objects.create(
                ingredient=ingredient,
                quantity=quantity,
                type=StockMovement.MovementType.OUT,
                user=self.request.user,
                notes=f"Waste Logged: {serializer.validated_data['reason']}"
            )

            serializer.save(
                recorded_by=self.request.user, 
                cost_at_time=cost_at_time
            )

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        from django.db.models import Sum, Count
        from django.db.models.functions import TruncDate
        from django.utils import timezone
        from datetime import timedelta

        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        logs = WasteLog.objects.filter(created_at__gte=start_date)

        # Total Wasted Value
        total_loss = sum((log.quantity * (log.cost_at_time or 0)) for log in logs)

        # Most requested reasons
        from django.db.models import Sum, Count
        reasons = logs.values('reason').annotate(
            count=Count('id'),
            total_qty=Sum('quantity')
        ).order_by('-total_qty')

        # Waste by ingredient
        ingredients_waste = logs.values('ingredient__name').annotate(
            total_qty=Sum('quantity')
        ).order_by('-total_qty')[:10]
        
        # Trend Over Time
        trends = logs.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total_qty=Sum('quantity')
        ).order_by('date')

        return Response({
            'total_financial_loss': float(total_loss),
            'logs_count': logs.count(),
            'reasons_distribution': reasons,
            'top_wasted_ingredients': ingredients_waste,
            'trends': trends
        })


