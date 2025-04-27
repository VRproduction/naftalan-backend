from django.db import migrations, models

def convert_booking_status(apps, schema_editor):
    Booking = apps.get_model('booking', 'Booking')
    
    # Map old status values to new status values
    status_mapping = {
        'pending': 'new',
        'awaiting_confirmation': 'new',
        'confirmed': 'confirmed',
        'cancelled': 'cancelled',
        'completed': 'completed',
        'client_contacted': 'new',
        'payment_pending': 'waiting_payment',
        'no_answer': 'new',
    }
    
    # Update all existing bookings to match the new statuses
    for old_status, new_status in status_mapping.items():
        Booking.objects.filter(status=old_status).update(status=new_status)

class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0007_simplify_booking_status'),
    ]

    operations = [
        migrations.RunPython(convert_booking_status, migrations.RunPython.noop),
    ] 