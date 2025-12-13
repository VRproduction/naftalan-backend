import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext as _, override as translation_override
from django.urls import reverse
from celery import shared_task
from django.db import transaction

from .models import PackageOrder

logger = logging.getLogger(__name__)


def get_translated_subject(status, package_name, language='az'):
    """Get translated email subject based on status"""
    subjects = {
        'pending': _("Paket sifarişiniz qəbul edildi - %(package)s"),
        'confirmed': _("Paket sifarişiniz təsdiqləndi - %(package)s"),
        'cancelled': _("Paket sifarişiniz ləğv edildi - %(package)s"),
        'completed': _("Paket sifarişiniz tamamlandı - %(package)s"),
    }
    with translation_override(language):
        return subjects.get(status, '') % {'package': package_name}


def get_admin_subject(first_name, last_name, language='az'):
    """Get translated admin email subject"""
    with translation_override(language):
        return _("Yeni paket sifarişi - %(name)s") % {'name': f"{first_name} {last_name}"}


@shared_task(bind=True, max_retries=3)
def send_package_order_email(self, order_id, old_status=None):
    """
    Send email notifications when a package order is created or status changes
    """
    try:
        with transaction.atomic():
            order = PackageOrder.objects.select_for_update().get(id=order_id)
            
            # Double check if status has changed since task was queued
            if old_status is not None and order.status == old_status:
                logger.info(f"Package order {order_id} status hasn't changed since task was queued")
                return True
        
        # Get language from order or use default
        language = getattr(order, 'language', settings.LANGUAGE_CODE)
        
        # Handle different status changes with appropriate templates and recipients
        if order.status == 'pending':
            # New order - send confirmation to customer and notification to admin
            send_customer_email(
                order=order, 
                subject=get_translated_subject('pending', order.package.name, language),
                template='emails/package_order_confirmation.html',
                language=language,
            )
            
            send_admin_email(
                order=order, 
                subject=get_admin_subject(order.first_name, order.last_name),
                template='emails/admin_new_package_order.html',
            )
            
        elif order.status == 'confirmed':
            # Order confirmed - send confirmation to customer
            send_customer_email(
                order=order, 
                subject=get_translated_subject('confirmed', order.package.name, language),
                template='emails/package_order_confirmed.html',
                language=language,
            )
            
        elif order.status == 'cancelled':
            # Order cancelled - notify customer
            send_customer_email(
                order=order, 
                subject=get_translated_subject('cancelled', order.package.name, language),
                template='emails/package_order_cancelled.html',
                language=language,
            )
            
        elif order.status == 'completed':
            # Order completed - thank you email to customer
            send_customer_email(
                order=order, 
                subject=get_translated_subject('completed', order.package.name, language),
                template='emails/package_order_completed.html',
                language=language,
            )
        
        return True
            
    except PackageOrder.DoesNotExist:
        logger.error(f"Package order with ID {order_id} not found.")
        return False
    except Exception as exc:
        logger.error(f"Error sending package order email for order {order_id}: {str(exc)}")
        # Retry the task with exponential backoff
        self.retry(exc=exc, countdown=2 ** self.request.retries)


def send_customer_email(order, subject, template, language='az'):
    """Helper function to send email to the customer"""
    if not order.email:
        logger.error(f"No email address for package order {order.id}")
        return False
    
    context = {
        'order': order,
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
            to=[order.email],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        logger.info(f"Customer email sent for package order {order.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send customer email for package order {order.id}: {str(e)}")
        return False


def send_admin_email(order, subject, template, language='az'):
    """Helper function to send email to admin(s)"""
    admin_emails = [email for name, email in settings.ADMINS]
    if not admin_emails:
        admin_emails = [settings.DEFAULT_FROM_EMAIL]
    
    # Try to generate admin URL, fallback to None if URL doesn't exist
    admin_url = None
    try:
        admin_url = settings.SITE_URL + reverse('admin:packages_packageorder_change', args=[order.id])
    except Exception:
        logger.warning(f"Could not generate admin URL for package order {order.id}")
    
    context = {
        'order': order,
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
        logger.info(f"Admin email sent for package order {order.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send admin email for package order {order.id}: {str(e)}")
        return False
