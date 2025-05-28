# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.db.models import Sum
# from .models import current_stock_data_master, inward_details, outward_details

# @receiver(post_save, sender=inward_details)
# @receiver(post_save, sender=outward_details)
# def update_stock(sender, instance, **kwargs):
#     # Get the spare_id from the saved instance
#     spare_id = instance.spare_id

#     # Calculate total inward quantity for this spare
#     total_in = inward_details.objects.filter(spare_id=spare_id).aggregate(
#         total_in=Sum('invoice_quantity')
#     )['total_in'] or 0  # Handle None case

#     # Calculate total outward quantity for this spare
#     total_out = outward_details.objects.filter(spare_id=spare_id).aggregate(
#         total_out=Sum('out_quantity')
#     )['total_out'] or 0  # Handle None case

#     # Calculate remaining stock
#     remaining_quantity = total_in - total_out

#     # Update or create the stock record
#     current_stock_data_master.objects.update_or_create(
#         spare_id=spare_id,
#         defaults={
#             'total_quantity': remaining_quantity,
#             'spare_name': instance.spare_name # Propagate name from the latest transaction
#         }
#     )