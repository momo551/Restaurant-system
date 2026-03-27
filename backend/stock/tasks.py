from celery import shared_task
import logging
from django.db.models import F
from .models import Ingredient, LowStockAlert

logger = logging.getLogger(__name__)

@shared_task
def check_low_stock():
    """
    Checks for ingredients that have fallen below their reorder_level.
    Generates LowStockAlert records for new shortages.
    """
    logger.info("Executing check_low_stock task...")
    
    # Ingredients that need restocking
    low_stock_ingredients = Ingredient.objects.filter(quantity__lte=F('reorder_level'), is_active=True)
    
    alerts_created = 0
    for ingredient in low_stock_ingredients:
        # Check if an unresolved alert already exists for this ingredient
        alert_exists, created = LowStockAlert.objects.get_or_create(
            ingredient=ingredient,
            is_resolved=False
        )
        
        if created:
            alerts_created += 1
            logger.info(f"Low stock alert generated for: {ingredient.name}")
            
            # Send an email to the supplier/managers
            # send_mail(...)

    # Auto-resolve alerts for ingredients whose stock has been replenished
    replenished_alerts = LowStockAlert.objects.filter(
        is_resolved=False,
        ingredient__quantity__gt=F('ingredient__reorder_level')
    )
    
    alerts_resolved = replenished_alerts.update(is_resolved=True)
    if alerts_resolved > 0:
        logger.info(f"Auto-resolved {alerts_resolved} stock alerts.")
        
    return f"Created {alerts_created} new alerts, resolved {alerts_resolved}."
