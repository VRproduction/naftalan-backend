import logging
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from celery import shared_task

from .models import Booking, BookingStatus

logger = logging.getLogger(__name__)

@shared_task
def send_booking_status_email(booking_id, old_status=None):
    """
    Send email notifications when a booking status changes
    """
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        logger.error(f"Booking with ID {booking_id} not found.")
        return False
    
    # Determine recipients based on status
    admin_emails = [email for name, email in settings.ADMINS]
    
    # Handle different status changes with appropriate templates and recipients
    if booking.status == BookingStatus.NEW:
        # New booking - send confirmation to customer and notification to admin
        send_customer_email(
            booking=booking, 
            subject=f"Rezervasiya qəbul edildi - {booking.booking_reference}",
            template='emails/booking_confirmation.html',
        )
        
        send_admin_email(
            booking=booking, 
            subject=f"Yeni rezervasiya - {booking.booking_reference}",
            template='emails/admin_new_booking.html',
        )
        
    elif booking.status == BookingStatus.CONFIRMED:
        # Booking confirmed - send confirmation to customer
        send_customer_email(
            booking=booking, 
            subject=f"Rezervasiyanız təsdiqləndi - {booking.booking_reference}",
            template='emails/booking_confirmed.html',
        )
        
    elif booking.status == BookingStatus.CANCELLED:
        # Booking cancelled - notify customer
        send_customer_email(
            booking=booking, 
            subject=f"Rezervasiyanız ləğv edildi - {booking.booking_reference}",
            template='emails/booking_cancelled.html',
        )
        
    elif booking.status == BookingStatus.WAITING_PAYMENT:
        # Payment pending - send payment instructions to customer
        send_customer_email(
            booking=booking, 
            subject=f"Ödəniş tələb olunur - {booking.booking_reference}",
            template='emails/payment_instructions.html',
        )
        
    elif booking.status == BookingStatus.COMPLETED:
        # Booking completed - thank you email to customer
        send_customer_email(
            booking=booking, 
            subject=f"Rezervasiyanız tamamlandı - {booking.booking_reference}",
            template='emails/booking_completed.html',
        )
    
    return True

def send_customer_email(booking, subject, template):
    """Helper function to send email to the customer"""
    if not booking.email:
        logger.error(f"No email address for booking {booking.booking_reference}")
        return False
    
    context = {
        'booking': booking,
        'booking_url': settings.SITE_URL + reverse('booking-detail', args=[booking.booking_reference]),
        'support_email': settings.DEFAULT_FROM_EMAIL,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    }
    
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)
    
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        logger.info(f"Customer email sent for booking {booking.booking_reference}")
        return True
    except Exception as e:
        logger.error(f"Failed to send customer email for booking {booking.booking_reference}: {str(e)}")
        return False

def send_admin_email(booking, subject, template):
    """Helper function to send email to admin(s)"""
    admin_emails = [email for name, email in settings.ADMINS]
    if not admin_emails:
        admin_emails = [settings.DEFAULT_FROM_EMAIL]
    
    context = {
        'booking': booking,
        'admin_url': settings.SITE_URL + reverse('admin:booking_booking_change', args=[booking.id]),
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    }
    
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)
    
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=admin_emails,
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        logger.info(f"Admin email sent for booking {booking.booking_reference}")
        return True
    except Exception as e:
        logger.error(f"Failed to send admin email for booking {booking.booking_reference}: {str(e)}")
        return False 