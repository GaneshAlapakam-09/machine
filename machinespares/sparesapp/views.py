from io import BytesIO
from time import localtime
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
import openpyxl
from.models import UserImage, preventive_work, spare_details,inward_details,outward_details,machine_details,current_stock_data_master,current_stock_data_details,inward_masters,BreakdownDetail,BreakdownMaster,spares_add_machine,minimum_stock_quantity_master,minimum_stock_quantity_details,minimum_stocks_quantity_master,minimum_stocks_quantity_details,preventive_work_details
from django.db.models import Sum
import json
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, JsonResponse
from django.db import transaction 
# from datetime import datetime
from.forms import SpareForm  
from openpyxl.utils import get_column_letter
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from datetime import datetime
import json
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view,parser_classes
from rest_framework.parsers import MultiPartParser, FormParser


# <-------- Machine Details ---------->

def dashboard(request):
    return render(request,'dashboard.html')

def add_machine(request):
    if request.method == "POST":
        machine_name = request.POST['machine_name']
        machine_make = request.POST['machine_make']
        machine_model = request.POST['machine_model']
        capacity = request.POST['capacity']
        spec1 = request.POST['spec1']
        spec2 = request.POST['spec2']
        spec3 = request.POST['spec3']
        spec4 = request.POST['spec4']
        spec5 = request.POST['spec5']
    
        last_machine = machine_details.objects.order_by('-machine_id').first()
        if last_machine:
            last_id = int(last_machine.machine_id[3:])
            new_id = f"MAC{last_id + 1:04d}"
        else:
            new_id = "MAC0001"

        machine_details.objects.create(machine_id = new_id, machine_name =machine_name, machine_make = machine_make, machine_model = machine_model, capacity = capacity, specification1 = spec1, specification2 = spec2, specification3 = spec3, specification4 = spec4, specification5 = spec5)
        return redirect('list_machine')
    last_machine = machine_details.objects.order_by('-machine_id').first()
    if last_machine:
        last_id = int(last_machine.machine_id[3:])
        new_id = f"MAC{last_id + 1:04d}"
    else:
        new_id = "MAC0001"
    context = {'new_id' : new_id}
    
    return render(request,'add_machine.html',context)

def list_machine(request):
    data = machine_details.objects.all()
    context = {'data':data}
    return render(request,'list_machine.html',context)


def add_spares(request):
    if request.method == 'POST':
        spare_id=request.POST['spare_id']
        spare_name=request.POST['spare_name']
        spare_make=request.POST['spare_make']
        specification_i=request.POST['specification_i']
        specification_ii=request.POST['specification_ii']
        specification_iii=request.POST['specification_iii']
        specification_iv=request.POST['specification_iv']

        last_spare=spare_details.objects.order_by('-spare_id').first()
        if last_spare:
            old_id=int(last_spare.spare_id[2:])
            auto_increament=f"SP{old_id+1:04d}"
        else:
            auto_increament="SP0001"

        spare_details.objects.create(spare_id=spare_id,spare_name=spare_name,spare_make=spare_make,specification_I=specification_i,specification_II=specification_ii,specification_III=specification_iii,specification_IV=specification_iv)
        
    

    last_spare=spare_details.objects.order_by('-spare_id').first()
    if last_spare:
        old_id=int(last_spare.spare_id[2:])
        auto_increament=f"SP{old_id+1:04d}"
    else:
        auto_increament="SP0001"
    
    context={'new_id':auto_increament}
    return render(request,'add_spares.html',context)

def list_spares(request):
    spare_parts=spare_details.objects.filter(status=1)
    context={'parts':spare_parts}
    return render(request,'list_spares.html',context)

# <-------- Spare Details ---------->

# ***********************************

def inward_adding(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))  # Parse JSON data
        # Generate unique inward_id and batch_id
        last_inward = inward_masters.objects.order_by('-inward_id').first()
        new_inward_id = f"IN{(int(last_inward.inward_id[2:]) + 1):04d}" if last_inward else "IN0001"

        last_batch = inward_masters.objects.order_by('-batch_id').first()
        new_batch_id = f"BATCH{(int(last_batch.batch_id[5:]) + 1):04d}" if last_batch else "BATCH0001"

        master = inward_masters.objects.create(
                inward_id=new_inward_id,
                batch_id=new_batch_id,
                invoice_id=data.get('invoice_id', ''),
                vendor_name=data.get('vendor_name', ''),
                vendor_phone=data.get('vendor_phone', ''),
                vendor_gst=data.get('vendor_gst', ''),
                grand_total=data.get('grand_total', 0),
                date=date.today()
            )
        spare_entries = data.get('spare_entries', [])
        if not spare_entries:
            return JsonResponse({'status': 'error', 'message': 'No spare entries provided'}, status=400)
        for item in spare_entries:
            spare_id = item.get('spare_id')
            spare_name = item.get('spare_name')
            invoice_cost = item.get('invoice_cost', 0)
            invoice_quantity = item.get('invoice_quantity', 0)
            cost_per_quantity = item.get('cost_per_quantity', 0)

            if not spare_id or not spare_name:
                return JsonResponse({'status': 'error', 'message': 'Missing spare_id or spare_name'}, status=400)
            inward_details.objects.create(
                    inward_id=master.inward_id,
                    batch_id=master.batch_id,
                    invoice_id=master.invoice_id,
                    spare_id=spare_id,
                    spare_name=spare_name,
                    vendor_name=master.vendor_name,
                    vendor_phone=master.vendor_phone,
                    vendor_gst=master.vendor_gst,
                    invoice_cost=invoice_cost,
                    invoice_quantity=invoice_quantity,
                    cost_per_quantity=cost_per_quantity,
                    date=date.today()
                )
            existing = current_stock_data_master.objects.get(spare_id=spare_id)
            if existing:
                updated_quantity = existing.total_quantity + invoice_quantity
                current_stock_data_master.objects.filter(spare_id=spare_id).update(total_quantity = updated_quantity)
                current_stock_data_details.objects.create(spare_id=spare_id,spare_name=spare_name,type='INWARD',total_quantity=invoice_quantity)
            else:
                current_stock_data_master.objects.create(spare_id=spare_id,spare_name=spare_name,total_quantity=invoice_quantity)
                current_stock_data_details.objects.create(spare_id=spare_id,type='INWARD',spare_name=spare_name,total_quantity=invoice_quantity)
        
        return JsonResponse({'status': 'success', 'message': 'Data saved successfully'})


        

    last_inward = inward_masters.objects.order_by('-inward_id').first()
    new_id = f"IN{(int(last_inward.inward_id[2:]) + 1):04d}" if last_inward else "IN0001"

    last_batch = inward_masters.objects.order_by('-batch_id').first()
    fresh_id = f"BATCH{(int(last_batch.batch_id[5:]) + 1):04d}" if last_batch else "BATCH0001"

    auto = spare_details.objects.all()

    context = {
        'new_id': new_id,
        'fresh_id': fresh_id,
        'auto': auto
    }
    return render(request,'add_inward.html',context)


def list_inward(request):
    data=inward_masters.objects.filter(status=1)
    context={'data':data}
    return render(request,'list_inward.html',context)


def details_of_inward(request,id):
    data = inward_details.objects.filter(inward_id = id)
    context = {'data':data}
    return render(request,'inward_details.html',context)


# <-------- Inward Details ---------->

# ************************************

# <-------- Outward Details --------->

def add_outward(request):
    if request.method=='POST':
        outward_id=request.POST['outward_id']
        machine_detail=request.POST['machine_detail']
        machine_id,machine_name=machine_detail.split(' --- ')
        select_spare=request.POST['select_spare']
        spare_id,spare_name=select_spare.split(' --- ')
        purpose=request.POST['purpose']
        out_quantity=request.POST['out_quantity']
        date=request.POST['date']
        minimum_stock_quantity=request.POST['minimum_stock_quantity']
        outward_details.objects.create(outward_id=outward_id,machine_id=machine_id,machine_name=machine_name,spare_id=spare_id,spare_name=spare_name,purpose=purpose,out_quantity=out_quantity,date=date,minimum_stock_quantity=minimum_stock_quantity)
        current_stock_data_details.objects.create(spare_id=spare_id,spare_name=spare_name,total_quantity=out_quantity,type="outward",date=date)
        return redirect('list_outward')
    
    outward=outward_details.objects.order_by('-outward_id').first()
    if outward:
        old_id=int(outward.outward_id[3:])
        new_id=f"OUT{old_id+1:04d}"
    else:
        new_id="OUT0001"
    

    trial= machine_details.objects.all()
    auto=spare_details.objects.all()

    context ={'new_id':new_id, 'data':trial,'auto':auto}
    return render(request,'add_outward.html',context)

def list_outward(request):
    store=BreakdownMaster.objects.all()
    context={'font':store}
    return render(request,'list_breakdown.html',context)

# <-------- Outward Details ---------->



def add_current_stock(request):
    if request.method=='POST':
        select_spare=request.POST['select_spare']
        spare_id,spare_name=select_spare.split(' --- ')       
        type=request.POST['type']
        date=request.POST['date']
        total_quantity=request.POST['total_quantity']
        minimum_stock_quantity=request.POST['minimum_stock_quantity']
        created_by=request.POST['created_by']
        
        total_inward = inward_details.objects.filter(spare_id=spare_id).aggregate(
            total=Sum('invoice_quantity')
        )['total'] or 0

        # Sum all outward quantities for this spare
        total_outward = outward_details.objects.filter(spare_id=spare_id).aggregate(
            total=Sum('out_quantity')
        )['total'] or 0

        # Calculate remaining stock
        remaining_quantity = total_inward - total_outward

        current_stock_data_master.objects.create(spare_id=spare_id,spare_name=spare_name,total_quantity=remaining_quantity,minimum_stock_quantity=minimum_stock_quantity)
        current_stock_data_details.objects.create(spare_id=spare_id,spare_name=spare_name,type=type,date=date,total_quantity=total_quantity,minimum_stock_quantity=minimum_stock_quantity,created_by=created_by)
        return redirect('list_current_stock')
 
    spare=spare_details.objects.all()
    context={'spare':spare}
    return render(request,context)


def list_stock_details(request):
    # Fetch all stock data
    part = current_stock_data_master.objects.all()

    # Prepare the data with calculated differences
    for item in part:
        item.difference_red = item.minimum_stock_quantity - item.total_quantity if item.total_quantity < item.minimum_stock_quantity else 0
        item.difference_green = item.total_quantity - item.minimum_stock_quantity if item.total_quantity > item.minimum_stock_quantity else 0
        item.difference_orange = 0 if item.total_quantity == item.minimum_stock_quantity else None

    return render(request, 'list_stock.html', {'part': part})



@csrf_exempt
def breakdown_adding(request, id):
    if request.method == "POST":
        try:
            # Generate new breakdown ID
            latest = BreakdownMaster.objects.order_by('-breakdown_id').first()
            if latest and latest.breakdown_id and latest.breakdown_id.startswith("BRK"):
                try:
                    old_id = int(latest.breakdown_id[3:])
                    new_breakdown_id = f"BRK{old_id + 1:04d}"
                except ValueError:
                    new_breakdown_id = "BRK0001"
            else:
                new_breakdown_id = "BRK0001"

            # Parse spare usage
            spares_json = request.POST.get("spares")
            if not spares_json:
                return JsonResponse({"message": "No spare data received."}, status=400)

            spares = json.loads(spares_json)

            # Check stock availability first
            for spare in spares:
                spare_id = spare.get("spare_id")
                qty_used = int(spare.get("quantity"))

                stock = current_stock_data_master.objects.filter(spare_id=spare_id).first()
                if not stock or stock.total_quantity < qty_used:
                    return JsonResponse({"message": f"Not enough stock for spare: {spare_id}"}, status=400)

            # Parse dates
            start_date = datetime.strptime(request.POST.get("start_date"), "%Y-%m-%dT%H:%M")
            end_date = datetime.strptime(request.POST.get("end_date"), "%Y-%m-%dT%H:%M")
            hours = round((end_date - start_date).total_seconds() / 3600, 2)

            # Create breakdown master
            master = BreakdownMaster.objects.create(
                breakdown_id=new_breakdown_id,
                machine_id=request.POST.get("machine_id"),
                machine_name=request.POST.get("machine_name"),
                machine_make=request.POST.get("machine_make"),
                start_date=start_date,
                end_date=end_date,
                shift=request.POST.get("shift"),
                causes_of_breakdown=request.POST.get("causes_of_breakdown"),
                technician_attend=request.POST.get("technician_attend"),
                operator_name=request.POST.get("operator_name"),
                hours=hours,
            )

            # Save breakdown details and handle image upload
            for index, spare in enumerate(spares):
                spare_id = spare.get("spare_id")
                spare_name = spare.get("spare_name")
                qty_used = int(spare.get("quantity"))

                image_field = request.FILES.get(f"spare_images_{index}")


                # Save breakdown detail
                BreakdownDetail.objects.create(
                    breakdown_id=master,
                    machine_id=request.POST.get("machine_id"),
                    machine_name=request.POST.get("machine_name"),
                    spare_id=spare_id,
                    spare_name=spare_name,
                    quantity=qty_used,
                    end_date=end_date,
                    image=image_field,
                    causes_of_breakdown=request.POST.get("causes_of_breakdown")
                )

                # Update stock
                stock = current_stock_data_master.objects.get(spare_id=spare_id)
                stock.total_quantity -= qty_used
                stock.save()

                current_stock_data_details.objects.create(
                    spare_id=spare_id,
                    spare_name=spare_name,
                    type='OUTWARD',
                    total_quantity=qty_used
                )

            return JsonResponse({"status": "success", "breakdown_id": new_breakdown_id})

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    # GET method (render the form)
    machine = get_object_or_404(machine_details, machine_id=id)
    auto = spare_details.objects.all()

    latest = BreakdownMaster.objects.order_by('-breakdown_id').first()
    if latest and latest.breakdown_id and latest.breakdown_id.startswith("BRK"):
        try:
            old_id = int(latest.breakdown_id[3:])
            new_breakdown_id = f"BRK{old_id + 1:04d}"
        except ValueError:
            new_breakdown_id = "BRK0001"
    else:
        new_breakdown_id = "BRK0001"

    context = {
        'machine': machine,
        'auto': auto,
        'new_breakdown_id': new_breakdown_id,
    }

    return render(request, 'breakdown_form.html', context)


@csrf_exempt
def breakdown_adding_production(request, id):
    if request.method == "POST":
        try:
            # Generate new breakdown ID
            latest = BreakdownMaster.objects.order_by('-breakdown_id').first()
            if latest and latest.breakdown_id and latest.breakdown_id.startswith("BRK"):
                try:
                    old_id = int(latest.breakdown_id[3:])
                    new_breakdown_id = f"BRK{old_id + 1:04d}"
                except ValueError:
                    new_breakdown_id = "BRK0001"
            else:
                new_breakdown_id = "BRK0001"

            # Parse dates
            start_date = datetime.strptime(request.POST.get("start_date"), "%Y-%m-%dT%H:%M")
            # end_date = datetime.strptime(request.POST.get("end_date"), "%Y-%m-%dT%H:%M")
            # hours = round((end_date - start_date).total_seconds() / 3600, 2)
            image_file = request.FILES['image']

            # Create breakdown master
            master = BreakdownMaster.objects.create(
                breakdown_id=new_breakdown_id,
                machine_id=request.POST.get("machine_id"),
                machine_name=request.POST.get("machine_name"),
                machine_make=request.POST.get("machine_make"),
                start_date=start_date,
                shift=request.POST.get("shift"),
                causes_of_breakdown=request.POST.get("causes_of_breakdown",''),
                operator_name=request.POST.get("operator_name"),
                damage_image = image_file
            )

            return JsonResponse({"status": "success", "breakdown_id": new_breakdown_id})

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    # GET method (render the form)
    machine = get_object_or_404(machine_details, machine_id=id)
    auto = spare_details.objects.all()

    latest = BreakdownMaster.objects.order_by('-breakdown_id').first()
    if latest and latest.breakdown_id and latest.breakdown_id.startswith("BRK"):
        try:
            old_id = int(latest.breakdown_id[3:])
            new_breakdown_id = f"BRK{old_id + 1:04d}"
        except ValueError:
            new_breakdown_id = "BRK0001"
    else:
        new_breakdown_id = "BRK0001"

    context = {
        'machine': machine,
        'auto': auto,
        'new_breakdown_id': new_breakdown_id,
    }

    return render(request, 'add_breakdown.html', context)





@csrf_exempt
def update_breakdown(request, id):
    if request.method == "POST":
        try:

            # Parse spare usage
            spares_json = request.POST.get("spares")
            if not spares_json:
                return JsonResponse({"message": "No spare data received."}, status=400)

            spares = json.loads(spares_json)

            # Check stock availability first
            for spare in spares:
                spare_id = spare.get("spare_id")
                qty_used = int(spare.get("quantity"))

                stock = current_stock_data_master.objects.filter(spare_id=spare_id).first()
                if not stock or stock.total_quantity < qty_used:
                    return JsonResponse({"message": f"Not enough stock for spare: {spare_id}"}, status=400)

            # Parse dates
            start_date = datetime.strptime(request.POST.get("start_date"), "%Y-%m-%dT%H:%M")
            end_date = datetime.strptime(request.POST.get("end_date"), "%Y-%m-%dT%H:%M")
            hours = round((end_date - start_date).total_seconds() / 3600, 2)

            # Create breakdown master
            master = BreakdownMaster.objects.filter(breakdown_id = id).update(
                breakdown_id = id,
                machine_id=request.POST.get("machine_id"),
                machine_name=request.POST.get("machine_name"),
                machine_make=request.POST.get("machine_make"),
                start_date=start_date,
                end_date=end_date,
                shift=request.POST.get("shift"),
                causes_of_breakdown=request.POST.get("causes_of_breakdown"),
                technician_attend=request.POST.get("technician_attend"),
                operator_name=request.POST.get("operator_name"),
                hours=hours,
                Breakdown_Status = 0

            )

            breakdown_master_instance = BreakdownMaster.objects.get(breakdown_id=id)


            

            # Save breakdown details and handle image upload
            for index, spare in enumerate(spares):
                spare_id = spare.get("spare_id")
                spare_name = spare.get("spare_name")
                qty_used = int(spare.get("quantity"))

                image_field = request.FILES.get(f"spare_images_{index}")


                # Save breakdown detail
                BreakdownDetail.objects.create(
                    breakdown_id=breakdown_master_instance,
                    machine_id=request.POST.get("machine_id"),
                    machine_name=request.POST.get("machine_name"),
                    spare_id=spare_id,
                    spare_name=spare_name,
                    quantity=qty_used,
                    end_date=end_date,
                    image=image_field,
                    causes_of_breakdown=request.POST.get("causes_of_breakdown")
                )

                # Update stock
                stock = current_stock_data_master.objects.get(spare_id=spare_id)
                stock.total_quantity -= qty_used
                stock.save()

                current_stock_data_details.objects.create(
                    spare_id=spare_id,
                    spare_name=spare_name,
                    type='OUTWARD',
                    total_quantity=qty_used
                )

            return JsonResponse({"status": "success", "breakdown_id": id})

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    # GET method (render the form)
    machine = get_object_or_404(BreakdownMaster, breakdown_id=id)
    auto = spare_details.objects.all()

    context = {
        'machine': machine,
        'auto': auto,
        'new_breakdown_id': id,
    }

    return render(request, 'update_breakdown.html', context)






def overall_machine(request, machine_id):
    machine_detail = machine_details.objects.get(machine_id=machine_id)

    # Filter breakdowns for the selected machine and order them
    breakdowns = BreakdownMaster.objects.filter(machine_id=machine_id).order_by('-start_date')

    # Spare parts used in those breakdowns
    spare_details = BreakdownDetail.objects.filter(breakdown_id__machine_id=machine_id)
    

    context = {
        'machine_detail': machine_detail,
        'breakdowns': breakdowns,
        'spare_details': spare_details,
    }
    return render(request, 'overall_machines.html', context)

def spare_detail(request, spare_id):  
    link =get_object_or_404(spare_details , spare_id=spare_id)
    context = {'spare': link}  
    return render(request, 'details_spare.html', context)

def spare_edit(request, spare_id):
    if request.method == 'POST':
        if request.method == 'POST':
            spare_name=request.POST['spare_name']
            spare_make=request.POST['spare_make']
            specification_i=request.POST['specification_i']
            specification_ii=request.POST['specification_ii']
            specification_iii=request.POST['specification_iii']
            specification_iv=request.POST['specification_iv']
            spare_details.objects.filter(spare_id=spare_id).update(spare_name=spare_name,spare_make=spare_make,specification_I=specification_i,specification_II=specification_ii,specification_III=specification_iii,specification_IV=specification_iv)
            return redirect('list_spares')

    data = spare_details.objects.get(spare_id=spare_id)
    context = {'spare':data}

    return render(request, 'edit_spare.html',context)

def delete_spare(request, spare_id):
    spare_details.objects.filter(spare_id = spare_id).update(status = 0)
    messages.info(request,'spare deleted')
    return redirect('list_spares')

def spare_add(request, machine_id):
    machine = get_object_or_404(machine_details, machine_id=machine_id)
    
    if request.method == 'POST':
        try:
            # Extract form data
            select_spare = request.POST['select_spare']
            spare_id, spare_name = select_spare.split(' --- ')
            spare_importance = request.POST['spare_importance']  # Changed to match your radio button name
            quantities_used = request.POST['quantities_used']

            # Create new entry
            new_spare = spares_add_machine.objects.create(
                spare_id=spare_id,
                spare_name=spare_name,
                spare_importance=spare_importance,  # Note: Check spelling in your model
                quantities_used=quantities_used,
                status=1
            )

            # Handle AJAX response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'spare_id': new_spare.spare_id,
                    'spare_name': new_spare.spare_name,
                    'spare_importance': new_spare.spare_importance,
                    'quantities_used': new_spare.quantities_used
                })
            
            # Non-AJAX fallback
            list = spares_add_machine.objects.filter(status=1)
            return render(request, 'spares_add.html', {'list': list, 'machine': machine})

        except ValueError as e:
            error = f"Invalid spare format: {str(e)}"
        except KeyError as e:
            error = f"Missing field: {str(e)}"
        except Exception as e:
            error = f"Error creating spare: {str(e)}"

        # Error handling for AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': error
            }, status=400)
        
        # Fallback error handling for non-AJAX
        list = spares_add_machine.objects.filter(status=1)
        return render(request, 'spares_add.html', {
            'list': list,
            'machine': machine,
            'error': error
        })

    # GET request handling
    list = spares_add_machine.objects.filter(status=1,machine_id = machine_id)
    spare=spare_details.objects.all()
    return render(request, 'spares_add.html', {'list': list, 'machine': machine,'spare':spare})

@csrf_exempt
def assign_spare_to_machine(request, machine_id):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            # Get machine and spare data from the request body
            machine_id = data.get("machine_id")  # It could be in the URL or data
            machine_name = data.get("machine_name")
            machine_make = data.get("machine_make")
            machine_model = data.get("machine_model")  # Assuming the model is passed in the request
            spares = data.get("spares", [])

            if not spares:
                return JsonResponse({"error": "No spares provided"}, status=400)

            # Loop through the list of spares to assign each spare
            for spare in spares:
                spare_id = spare.get("spare_id")
                spare_name = spare.get("spare_name")
                spare_importance = spare.get("spare_importance")
                quantities_used = int(spare.get("quantities_used", 0))

                # ✅ 1. Create a new record in spares_add_machine
                spares_add_machine.objects.create(
                    machine_id=machine_id,
                    machine_name=machine_name,
                    machine_make=machine_make,
                    machine_model=machine_model,  # Correctly pass machine_model here
                    spare_id=spare_id,
                    spare_name=spare_name,
                    spare_importance=spare_importance,
                    quantities_used=quantities_used,
                    status=1  # Set the status (can be dynamic if needed)
                )

                # ✅ 2. Create a new row in minimum_stocks_quantity_details
                minimum_stocks_quantity_details.objects.create(
                    machine_id=machine_id,
                    machine_name=machine_name,
                    machine_make=machine_make,
                    spare_id=spare_id,
                    spare_name=spare_name,
                    spare_importance=spare_importance,
                    quantities_used=quantities_used,
                )

                # ✅ 3. Update or create the entry in minimum_stocks_quantity_master
                try:
                    master_obj = minimum_stocks_quantity_master.objects.get(
                        spare_id=spare_id,
                        spare_name=spare_name
                    )
                    master_obj.quantities_used += quantities_used
                    master_obj.save()
                    updated_quantity_used = master_obj.quantities_used
                except minimum_stocks_quantity_master.DoesNotExist:
                    new_master = minimum_stocks_quantity_master.objects.create(
                        spare_id=spare_id,
                        spare_name=spare_name,
                        quantities_used=quantities_used,
                        status=1
                    )
                    updated_quantity_used = new_master.quantities_used

                # ✅ 4. Update or create the entry in current_stock_data_master
                try:
                    stock_obj = current_stock_data_master.objects.get(spare_id=spare_id)
                    stock_obj.minimum_stock_quantity = updated_quantity_used
                    stock_obj.save()
                except current_stock_data_master.DoesNotExist:
                    current_stock_data_master.objects.create(
                        spare_id=spare_id,
                        spare_name=spare_name,
                        total_quantity=0,
                        minimum_stock_quantity=updated_quantity_used,
                        status=1
                    )

            return JsonResponse({"success": True, "message": "Spares assigned successfully!"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
def breakdownDetails(request,id):
    store=BreakdownDetail.objects.filter(breakdown_id=id)
    data=BreakdownMaster.objects.filter(breakdown_id=id)
    context={'font':store,'data':data}
    return render(request,'break_details.html',context)

def breakdown_detail_view(request, breakdown_id):
    breakdown = get_object_or_404(BreakdownMaster, breakdown_id=breakdown_id)
    machine = machine_details.objects.get(machine_id=breakdown.machine_id) 
    spare_details = BreakdownDetail.objects.filter(breakdown_id=breakdown_id)

    return render(request, 'breakdown_details.html', {
        'breakdown': breakdown,
        'machine': machine,
        'spare_details': spare_details
    })



def list_spare(request, machine_id):
    machine = get_object_or_404(machine_details, machine_id=machine_id)

    
    # ✅ FIXED this line: no ForeignKey, so just filter by the field directly
    spares = spares_add_machine.objects.filter(machine_id=machine_id)

    context = {
        'machine': machine,
        'spares': spares
    }
    return render(request, 'list_sparing.html', context)


def list_breakdowns(request, machine_id):
    machine = machine_details.objects.get(machine_id=machine_id)

    # Get breakdown detail entries where master is related to this machine
    details = BreakdownDetail.objects.filter(breakdown_d=machine.breakdown_id)

    return render(request, 'list_breakdowns.html', {
        'machine': machine,
        'details': details,
    })



def breakdown_report(request, machine_id=None):
    # Get all breakdowns (modified from your existing code)
    breakdowns = BreakdownMaster.objects.all()  # Remove machine_id filter
    
    # Export functionality
    download_format = request.GET.get('download')
    if download_format:
        # Common data preparation
        data = [['Machine ID', 'Machine Name', 'Start Date', 'End Date', 
                'Duration (Hrs)', 'Shift','Cause of Breakdown','Technician', 'Operator']]
        
        for bd in breakdowns:
            start = localtime(bd.start_date).strftime('%d-%m-%Y %H:%M')
            end = localtime(bd.end_date).strftime('%d-%m-%Y %H:%M')
            data.append([
                bd.machine_id,
                bd.machine_name,
                start,
                end,
                f"{bd.hours:.2f}",
                bd.shift,
                bd.causes_of_breakdown,
                bd.technician_attend,
                bd.operator_name
            ])


        if download_format == 'excel':
            return generate_excel(data)
    dateTime = datetime.now()

    context = {
        'breakdowns': breakdowns,
        'machine_detail': None , # Remove machine-specific data
        'dateTime':dateTime
    }
    return render(request, 'bd_report.html', context)



def generate_excel(data):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Breakdown Report"
    
    # Add data
    for row in data:
        ws.append(row)
    
    # Styling header
    header = ws[1]
    for cell in header:
        cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
        cell.fill = openpyxl.styles.PatternFill(
            start_color="4472C4", 
            end_color="4472C4", 
            fill_type="solid"
        )
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column[0].column_letter].width = adjusted_width
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="breakdown_report.xlsx"'
    return response
   

   
def spares_inward_report(request):
    # Get all inward details
    inspares = inward_details.objects.filter(status=1)
    
    # Export functionality
    download_format = request.GET.get('download')
    if download_format:
        # Prepare data
        data = [[
            'Inward ID', 'Batch ID', 'Spare ID', 'Spare Name', 
            'Invoice ID', 'Vendor Name', 'Quantity', 'Cost' , 'Date'
        ]]
        
        for inward in inspares:
            data.append([
                inward.inward_id,
                inward.batch_id,
                inward.spare_id,
                inward.spare_name,
                inward.invoice_id,
                inward.vendor_name,
                str(inward.invoice_quantity),
                str(inward.invoice_cost),
                inward.date.strftime('%d-%m-%Y') if inward.date else ''
            ])

     
        if download_format == 'excel':
            return generate_inward_excel(data)
    dateTime = datetime.now()
    context = {'inspares': inspares,'dateTime':dateTime}
    return render(request, 'spin_report.html', context)


def spares_inward_report2(request):
    data = inward_details.objects.filter(status=1)
    context = {'data':data}
    return render(request,'spares_inward_report.html',context)



def generate_inward_excel(data):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inward Report"
    
    for row in data:
        ws.append(row)
    
    # Styling
    header = ws[1]
    for cell in header:
        cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
        cell.fill = openpyxl.styles.PatternFill(
            start_color="4472C4", 
            fill_type="solid"
        )
    
    # Set column widths
    column_widths = [15, 18, 15, 25, 18, 25, 12, 12, 15]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="inward_report.xlsx"'
    return response



def spares_outward_report(request):
    outwards = BreakdownDetail.objects.all()
    
    download_format = request.GET.get('download')
    if download_format:
        data = [[
            'Outward ID', 'Machine ID', 'Machine Name', 
            'Spare ID', 'Spare Name', 'Purpose', 
            'Quantity', 'Date'
        ]]
        
        for outward in outwards:
            data.append([
                outward.breakdown_id,
                outward.machine_id,
                outward.machine_name,
                outward.spare_id,
                outward.spare_name,
                outward.purpose,
                str(outward.out_quantity),
                outward.date.strftime('%d-%m-%Y') if outward.date else ''
            ])

        if download_format == 'excel':
            return generate_outward_excel(data)
        
    dateTime = datetime.now()

    context = {'outwards': outwards,'dateTime':dateTime}
    return render(request, 'spout_report.html', context)

def spares_outward_report2(request):
    data = BreakdownDetail.objects.all()
    context = {'data':data}
    return render(request,'spares_outward_report.html',context)





def generate_outward_excel(data):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Outward Report"
    
    for row in data:
        ws.append(row)
    
    # Styling
    header = ws[1]
    for cell in header:
        cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
        cell.fill = openpyxl.styles.PatternFill(
            start_color="4a6da7", 
            fill_type="solid"
        )
    
    # Set column widths
    column_widths = [15, 12, 18, 12, 20, 25, 10, 15]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="outward_report.xlsx"'
    return response

def add_preventive(request):
    if request.method == "POST":
        machine = request.POST.get('machine_hidden')
        machine_id , machine_name = machine.split('--')
        work_type = request.POST.get('type_of_work')
        work_cycle = request.POST.get('work_cycle')
        last_entry = preventive_work.objects.order_by('-preventive_id').first()
        if last_entry :
            old_id = int(last_entry.preventive_id[3:])
            auto_id = f"PVT{old_id + 1:04d}"
        else:
            auto_id = "PVT0001"

        preventive_work.objects.create(preventive_id = auto_id, machine_id = machine_id, machine_name = machine_name, type_of_work = work_type, work_cycle = work_cycle)
        
    last_entry = preventive_work.objects.order_by('-preventive_id').first()
    if last_entry :
        old_id = int(last_entry.preventive_id[3:])
        auto_id = f"PVT{old_id + 1:04d}"
    else:
        auto_id = "PVT0001"

    data = machine_details.objects.all()

    context = {'new_id':auto_id,'data':data}
    return render(request,'add_preventive.html',context)

def list_preventive(request):
    data = preventive_work.objects.all()
    context = {'data':data}
    return render(request,'list_preventive.html',context)


def breakdown_report2(request):
    data=BreakdownMaster.objects.all()
    data2=BreakdownDetail.objects.all()
    context={'data':data,'data2':data2}
    return render(request,'breakdown_report.html',context)



def check_preventive(request,id):
    if request.method == "POST":
        machine = request.POST.get('machine_details')
        machine_id , machine_name = machine.split('--')
        work_type = request.POST.get('type_of_work')
        work_cycle = request.POST.get('work_cycle')
        checked_by = request.POST.get('checked_by')

        preventive_work_details.objects.create(preventive_id = id ,machine_id = machine_id, machine_name = machine_name, type_of_work = work_type, work_cycle = work_cycle, checked_by = checked_by)
        
    data = preventive_work.objects.get(preventive_id = id)
    context ={'data':data}
    return render(request,'add_checking.html',context)

def detail_preventive(request,id):
    data = preventive_work_details.objects.filter(preventive_id = id)
    context = {'data':data}
    return render(request,'preventive_details.html',context)



# @method_decorator(csrf_exempt, name='dispatch')
# @login_required

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']

        image = UserImage.objects.create(image=image_file)
        return JsonResponse({'id': image.id, 'image_url': image.image.url, 'uploaded_at': image.uploaded_at})

    return render(request,'image_upload.html')
    # return HttpResponseBadRequest('Invalid request')



def list_images(request):
    images = BreakdownDetail.objects.all()
    

    return render(request, 'uploaded_image.html', {'images': images})



@csrf_exempt
def delete_images(request):
    if request.method == 'POST':
        ids = request.POST.getlist('images_to_delete')
        UserImage.objects.filter(id__in=ids).delete()
    return redirect('list_images')  # replace with your actual view name

@csrf_exempt
def machine_list_api(request):
    if request.method == "GET":
        machines = machine_details.objects.all()
        data = []
        for m in machines:
            data.append({
                "machine_id": m.machine_id.strip(),
                "machine_name": m.machine_name.strip(),
                "machine_make": m.machine_make.strip(),
                "machine_model": m.machine_model.strip(),
                "capacity": m.capacity,
            })
        return JsonResponse(data, safe=False)


@csrf_exempt
@parser_classes([MultiPartParser, FormParser])
def breakdown_adding_production_api(request):
    if request.method == "POST":
        try:
            # Generate new Breakdown ID
            latest = BreakdownMaster.objects.order_by('-breakdown_id').first()
            if latest and latest.breakdown_id and latest.breakdown_id.startswith("BRK"):
                try:
                    old_id = int(latest.breakdown_id[3:])
                    new_breakdown_id = f"BRK{old_id + 1:04d}"
                except ValueError:
                    new_breakdown_id = "BRK0001"
            else:
                new_breakdown_id = "BRK0001"

            # Parse start date
            start_date_str = request.POST.get("start_date")
            if not start_date_str:
                return JsonResponse({"error": "Start date is required"}, status=400)
            
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    return JsonResponse({"error": "Invalid date format"}, status=400)

            # Get image (optional)
            image_file = request.FILES.get('image')

            # Create BreakdownMaster record
            master = BreakdownMaster.objects.create(
                breakdown_id=new_breakdown_id,
                machine_id=request.POST.get("machine_id"),
                machine_name=request.POST.get("machine_name"),
                machine_make=request.POST.get("machine_make"),
                start_date=start_date,
                shift=request.POST.get("shift"),
                causes_of_breakdown=request.POST.get("causes_of_breakdown", ''),
                operator_name=request.POST.get("operator_name"),
                damage_image=image_file
            )

            return JsonResponse({"message": "Breakdown submitted successfully", "breakdown_id": new_breakdown_id})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse("Bad request", status=400)