from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q
from .models import DailyClosingReport
from orders.models import Order
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def run_auto_eod():
    """
    Runs automatically at the end of the day to calculate daily metrics,
    save the summary report, and notify the owner.
    """
    logger.info("Starting Auto EOD Task...")
    
    # Define today's boundaries
    now = timezone.now()
    today = now.date()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Check if a report for today already exists to prevent duplicates
    if DailyClosingReport.objects.filter(date=today).exists():
        logger.warning(f"Auto EOD Report for {today} already exists. Skipping.")
        return "Skipped - Already exists"

    # Fetch all completed orders for today
    completed_statuses = [Order.Status.SERVED, Order.Status.DELIVERED, Order.Status.PAID]
    today_orders = Order.objects.filter(
        created_at__range=[today_start, today_end],
        status__in=completed_statuses,
        is_deleted=False
    )
    
    stats = today_orders.aggregate(
        total_sales=Sum('total'),
        total_orders=Count('id')
    )
    
    total_sales = stats['total_sales'] or 0
    total_orders = stats['total_orders'] or 0
    
    cash_total = total_sales
    card_total = 0
    discount_total = 0
    
    average_order_value = total_sales / total_orders if total_orders > 0 else 0

    # Save to DailyClosingReport
    report = DailyClosingReport.objects.create(
        date=today,
        total_sales=total_sales,
        total_orders=total_orders,
        cash_total=cash_total,
        card_total=card_total,
        discount_total=discount_total,
        average_order_value=average_order_value
    )
    
    logger.info(f"Auto EOD Report created successfully for {today}.")
    
    # Prepare summary message
    summary_message = f"""
    Daily Restaurant Report - {today}
    
    Total Sales: {total_sales} EGP
    Total Orders: {total_orders}
    Cash Payments: {cash_total} EGP
    Card Payments: {card_total} EGP
    Discounts: {discount_total} EGP
    Average Order Value: {average_order_value:.2f} EGP
    """
    
    # Attempt to send email if configured
    try:
        from users.models import User
        # Get owner emails
        owners = User.objects.filter(role='owner', email__isnull=False).exclude(email='')
        owner_emails = [owner.email for owner in owners]
        
        if owner_emails and getattr(settings, 'EMAIL_HOST', None):
            send_mail(
                subject=f'Daily Restaurant Report - {today}',
                message=summary_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=owner_emails,
                fail_silently=True,
            )
            logger.info("Sent EOD email to owners.")
    except Exception as e:
        logger.error(f"Failed to send EOD email: {str(e)}")
        
    return f"Success - EOD for {today} completed."
