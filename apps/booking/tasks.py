import logging
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext as _, override as translation_override
from django.urls import reverse
from celery import shared_task
from django.db import transaction

from .models import Booking, BookingStatus

logger = logging.getLogger(__name__)


def get_translated_subject(status, booking_reference, language='az'):
    """Get translated email subject based on status"""
    subjects = {
        BookingStatus.NEW: _("Rezervasiya qəbul edildi - %(ref)s"),
        BookingStatus.CONFIRMED: _("Rezervasiyanız təsdiqləndi - %(ref)s"),
        BookingStatus.CANCELLED: _("Rezervasiyanız ləğv edildi - %(ref)s"),
        BookingStatus.WAITING_PAYMENT: _("Ödəniş tələb olunur - %(ref)s"),
        BookingStatus.COMPLETED: _("Rezervasiyanız tamamlandı - %(ref)s"),
    }
    with translation_override(language):
        return subjects.get(status, '') % {'ref': booking_reference}


def get_admin_subject(booking_reference, language='az'):
    """Get translated admin email subject"""
    with translation_override(language):
        return _("Yeni rezervasiya - %(ref)s") % {'ref': booking_reference}


@shared_task(bind=True, max_retries=3)
def send_booking_status_email(self, booking_id, old_status=None):
    """
    Send email notifications when a booking status changes
    """
    try:
        with transaction.atomic():
            booking = Booking.objects.select_for_update().get(id=booking_id)
            
            # Double check if status has changed since task was queued
            if old_status is not None and booking.status == old_status:
                logger.info(f"Booking {booking_id} status hasn't changed since task was queued")
                return True
        
        # Get language from booking or use default
        language = getattr(booking, 'language', settings.LANGUAGE_CODE)
        
        # Determine recipients based on status
        admin_emails = [email for name, email in settings.ADMINS]
        
        # Handle different status changes with appropriate templates and recipients
        if booking.status == BookingStatus.NEW:
            # New booking - send confirmation to customer and notification to admin
            send_customer_email(
                booking=booking, 
                subject=get_translated_subject(BookingStatus.NEW, booking.booking_reference, language),
                template='emails/booking_confirmation.html',
                language=language,
            )
            
            send_admin_email(
                booking=booking, 
                subject=get_admin_subject(booking.booking_reference),
                template='emails/admin_new_booking.html',
            )
            
        elif booking.status == BookingStatus.CONFIRMED:
            # Booking confirmed - send confirmation to customer
            send_customer_email(
                booking=booking, 
                subject=get_translated_subject(BookingStatus.CONFIRMED, booking.booking_reference, language),
                template='emails/booking_confirmed.html',
                language=language,
            )
            
        elif booking.status == BookingStatus.CANCELLED:
            # Booking cancelled - notify customer
            send_customer_email(
                booking=booking, 
                subject=get_translated_subject(BookingStatus.CANCELLED, booking.booking_reference, language),
                template='emails/booking_cancelled.html',
                language=language,
            )
            
        elif booking.status == BookingStatus.WAITING_PAYMENT:
            # Payment pending - send payment instructions to customer
            send_customer_email(
                booking=booking, 
                subject=get_translated_subject(BookingStatus.WAITING_PAYMENT, booking.booking_reference, language),
                template='emails/payment_instructions.html',
                language=language,
            )
            
        elif booking.status == BookingStatus.COMPLETED:
            # Booking completed - thank you email to customer
            send_customer_email(
                booking=booking, 
                subject=get_translated_subject(BookingStatus.COMPLETED, booking.booking_reference, language),
                template='emails/booking_completed.html',
                language=language,
            )
        
        return True
            
    except Booking.DoesNotExist:
        logger.error(f"Booking with ID {booking_id} not found.")
        return False
    except Exception as exc:
        logger.error(f"Error sending booking status email for booking {booking_id}: {str(exc)}")
        # Retry the task with exponential backoff
        self.retry(exc=exc, countdown=2 ** self.request.retries)


def send_customer_email(booking, subject, template, language='az'):
    """Helper function to send email to the customer"""
    if not booking.email:
        logger.error(f"No email address for booking {booking.booking_reference}")
        return False
    
    # Try to generate booking URL, fallback to None if URL doesn't exist
    booking_url = None
    try:
        booking_url = settings.SITE_URL + reverse('booking-detail', args=[booking.booking_reference])
    except Exception:
        logger.warning(f"Could not generate booking URL for {booking.booking_reference}")
    
    context = {
        'booking': booking,
        'booking_url': booking_url,
        'support_email': settings.DEFAULT_FROM_EMAIL,
        'site_name': getattr(settings, 'SITE_NAME', 'NAFTALAN-KURORT'),
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        'LANGUAGE_CODE': language,
    }
    
    # Render template with the correct language
    with translation_override(language):
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


def send_admin_email(booking, subject, template, language='az'):
    """Helper function to send email to admin(s)"""
    admin_emails = [email for name, email in settings.ADMINS]
    if not admin_emails:
        admin_emails = [settings.DEFAULT_FROM_EMAIL]
    
    # Try to generate admin URL, fallback to None if URL doesn't exist
    admin_url = None
    try:
        admin_url = settings.SITE_URL + reverse('admin:booking_booking_change', args=[booking.id])
    except Exception:
        logger.warning(f"Could not generate admin URL for booking {booking.id}")
    
    context = {
        'booking': booking,
        'admin_url': admin_url,
        'site_name': getattr(settings, 'SITE_NAME', 'NAFTALAN-KURORT'),
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        'LANGUAGE_CODE': language,
    }
    
    # Render template with the correct language
    with translation_override(language):
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
