from django.db import models

class machine_details(models.Model):
    machine_id = models.CharField(primary_key=True, max_length=50)
    machine_name = models.CharField(max_length=50, null=True)
    machine_make = models.CharField(max_length=50, null=True)
    machine_model = models.CharField(max_length=50, null=True)
    capacity = models.IntegerField(null=True)
    specification1 = models.CharField(max_length=50, null=True)
    specification2 = models.CharField(max_length=50, null=True)
    specification3 = models.CharField(max_length=50, null=True)
    specification4 = models.CharField(max_length=50, null=True)
    specification5 = models.CharField(max_length=50, null=True)


class spare_details(models.Model):
    spare_id=models.CharField(max_length=40,unique=True,null=True)
    spare_name=models.CharField(max_length=50,null=True)
    spare_make=models.CharField(max_length=30,null=True)
    specification_I=models.CharField(max_length=50,null=True)
    specification_II=models.CharField(max_length=50,null=True)
    specification_III=models.CharField(max_length=50,null=True)
    specification_IV=models.CharField(max_length=50,null=True)
    minimum_stock_quantity=models.IntegerField(default=0)
    status=models.IntegerField(default=1)

class inward_masters(models.Model):
    inward_id = models.CharField(max_length=20, primary_key=True)
    batch_id = models.CharField(max_length=20)
    invoice_id = models.CharField(max_length=50)
    vendor_name = models.CharField(max_length=100)
    vendor_phone = models.CharField(max_length=15)
    vendor_gst = models.CharField(max_length=30)
    grand_total = models.IntegerField(default=0)
    date = models.DateField(null=True)
    status = models.IntegerField(default=1)

class inward_details(models.Model):
    inward = models.ForeignKey(inward_masters, on_delete=models.CASCADE, to_field='inward_id')
    spare_id = models.CharField(max_length=20)
    spare_name = models.CharField(max_length=100)
    invoice_cost = models.FloatField()
    invoice_quantity = models.IntegerField()
    cost_per_quantity = models.FloatField()
    batch_id = models.CharField(max_length=20)
    invoice_id = models.CharField(max_length=50)
    vendor_name = models.CharField(max_length=100)
    vendor_phone = models.CharField(max_length=15)
    vendor_gst = models.CharField(max_length=30)
    date = models.DateField(null=True)
    
    status = models.IntegerField(default=1)

class outward_details(models.Model):
    outward_id=models.CharField(null=True, max_length=50)
    machine_id=models.CharField(max_length=50,null=True)
    machine_name=models.CharField(max_length=40,null=True)
    spare_id=models.CharField(max_length=40,null=True)
    spare_name=models.CharField(max_length=50,null=True)
    purpose=models.CharField(max_length=50,null=True) 
    out_quantity=models.IntegerField(null=True)
    minimum_stock_quantity=models.IntegerField(default=0)  
    date=models.DateField(null=True, auto_now=False, auto_now_add=False) 
    status=models.IntegerField(default=1)


class current_stock_data_master(models.Model):
    spare_id=models.CharField(max_length=50,primary_key=True)
    spare_name=models.CharField(max_length=50,null=True)
    total_quantity=models.IntegerField(null=True)
    minimum_stock_quantity=models.IntegerField(default=0)
    date = models.DateField( auto_now=True, auto_now_add=False)
    grand_total = models.IntegerField(default=0)
    status=models.IntegerField(default=1)

class current_stock_data_details(models.Model):
    spare_id=models.CharField(max_length=50,null=True)
    spare_name=models.CharField(max_length=50,null=True)
    type=models.CharField(max_length=50,null=True)
    date=models.DateField(auto_now=True, auto_now_add=False,null=True)
    total_quantity=models.IntegerField(null=True)
    status=models.IntegerField(default=1)


class BreakdownMaster(models.Model):
    breakdown_id=models.CharField(max_length=50,primary_key=True)
    machine_id = models.CharField(max_length=50, null=True)
    machine_name = models.CharField(max_length=100, null=True)
    machine_make = models.CharField(max_length=100, null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    hours=models.FloatField(null=True)
    shift = models.CharField(max_length=20, null=True)
    causes_of_breakdown = models.TextField(null=True)
    technician_attend = models.CharField(max_length=100, null=True)
    operator_name = models.CharField(max_length=100, null=True)
    damage_image = models.ImageField(upload_to='uploads/',null=True)
    Breakdown_Status = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.breakdown_id}"


class BreakdownDetail(models.Model):
    breakdown_id = models.ForeignKey("sparesapp.BreakdownMaster" , on_delete=models.CASCADE)
    machine_id = models.CharField(max_length=50, null=True)
    machine_name = models.CharField(max_length=100, null=True)
    causes_of_breakdown = models.TextField(null=True)
    spare_id = models.CharField(max_length=50, null=True)
    spare_name = models.CharField(max_length=100, null=True)
    quantity = models.IntegerField(null=True)
    end_date = models.DateTimeField(null=True)
    image = models.ImageField(upload_to='uploads/',null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"{self.spare_id} - {self.spare_name}"
    


class spares_add_machine(models.Model):
    machine_id = models.CharField(max_length=40, null=True)
    machine_name = models.CharField(max_length=50, null=True)
    machine_make = models.CharField(max_length=50, null=True)
    machine_model = models.CharField(max_length=50, null=True)
    spare_id=models.CharField(max_length=40,null=True)
    spare_name=models.CharField(max_length=50,null=True)
    spare_importance=models.CharField(max_length=50,null=True)
    quantities_used=models.IntegerField(null=True)
    status=models.IntegerField(default=1)  


class minimum_stock_quantity_master(models.Model):
    spare_id=models.CharField(max_length=40,unique=True,null=True)
    spare_name=models.CharField(max_length=50,null=True)
    quantities_used=models.IntegerField(null=True)
    status=models.IntegerField(null=True)



class minimum_stock_quantity_details(models.Model):
    machine_id = models.CharField(max_length=50, null=True)
    machine_name = models.CharField(max_length=100, null=True)
    machine_make = models.CharField(max_length=100, null=True)
    spare_id=models.CharField(max_length=40,unique=True,null=True)
    spare_name=models.CharField(max_length=50,null=True)
    spare_importance=models.CharField(max_length=50,null=True)
    quantities_used=models.IntegerField(null=True)



class minimum_stocks_quantity_master(models.Model):
    spare_id=models.CharField(max_length=40,unique=True,null=True)
    spare_name=models.CharField(max_length=50,null=True)
    quantities_used=models.IntegerField(null=True)
    status=models.IntegerField(null=True,default=1)
    date = models.DateField(auto_now=True, auto_now_add=False)



class minimum_stocks_quantity_details(models.Model):
    machine_id = models.CharField(max_length=50, null=True)
    machine_name = models.CharField(max_length=100, null=True)
    machine_make = models.CharField(max_length=100, null=True)
    spare_id=models.CharField(max_length=40,null=True)
    spare_name=models.CharField(max_length=50,null=True)
    spare_importance=models.CharField(max_length=50,null=True)
    quantities_used=models.IntegerField(null=True)



class preventive_work(models.Model):
    preventive_id=models.CharField(primary_key=True,max_length=50)
    machine_id = models.CharField(max_length=50, null=True)
    machine_name = models.CharField(max_length=50, null=True)
    type_of_work=models.CharField(max_length=50,null=True)
    work_cycle=models.CharField(max_length=50,null=True)
    status=models.IntegerField(null=True,default=1)


class preventive_work_details(models.Model):
    preventive_id = models.CharField(max_length=50)
    machine_id = models.CharField(max_length=50, null=True)
    machine_name = models.CharField(max_length=50, null=True)
    type_of_work=models.CharField(max_length=50,null=True)
    work_cycle=models.CharField(max_length=50,null=True)
    checked_by = models.CharField( max_length=50)
    date = models.DateField(auto_now=True, auto_now_add=False)
    status=models.IntegerField(null=True,default=1)


class UserImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)



class FCMToken(models.Model):
    username = models.CharField(max_length=150)
    token = models.CharField(max_length=512, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.token[:20]}"