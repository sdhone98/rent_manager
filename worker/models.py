import random
from django.db import models
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from resources.constant import ElectricityConsumer
from resources.custom_enums import (
    RoleChoices,
    StateCode,
    FloorCodes,
    BuildingCodes,
    PaymentModeChoices,
    NoticeType
)


class Person(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    f_name = models.CharField(max_length=75)
    m_name = models.CharField(max_length=75, null=True, blank=True)
    l_name = models.CharField(max_length=75)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    role = models.CharField(max_length=50, default=RoleChoices.TENANT, choices=RoleChoices.choices)
    ts = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "person"
        managed = True

    def __str__(self):
        return f"{self.f_name} {self.m_name} {self.l_name}"

    def get_full_name(self):
        return f"{self.f_name} {self.m_name} {self.l_name}"


class Contact(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="contacts", unique=True)
    phn_no = models.CharField(max_length=15, unique=True)
    alt_phn_no = models.CharField(max_length=15, null=True, blank=True)
    wa_no = models.CharField(max_length=15, unique=True)

    class Meta:
        db_table = "contact"
        managed = True


class Address(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="addresses", unique=True)
    old_add = models.TextField(max_length=255)
    st = models.CharField(max_length=50, choices=StateCode.choices, default=StateCode.MAHARASHTRA)
    ct = models.CharField(max_length=70)
    pn_code = models.BigIntegerField()

    class Meta:
        db_table = "address"
        managed = True


class Docs(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="docs", unique=True)
    aadhar_no = models.CharField(max_length=15, unique=True)
    aadhaar_doc = models.FileField(upload_to="documents/aadhaar/", null=True, blank=True)
    pan_no = models.CharField(max_length=255, unique=True)
    pan_doc = models.FileField(upload_to="documents/pan/", null=True, blank=True)

    class Meta:
        db_table = "docs"
        managed = True


class RoomMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    r_no = models.IntegerField()
    flr_no = models.CharField(max_length=20, choices=FloorCodes.choices)
    add = models.CharField(max_length=255, null=True, blank=True)
    build_name = models.CharField(max_length=50, choices=BuildingCodes.choices)
    r_code = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = "room_master"
        managed = True

    def save(self, *args, **kwargs):
        self.r_code = f"{self.r_no}_{self.build_name}"

        # SAVE ADDRESS
        if self.build_name == BuildingCodes.VAMAN_NIVAS:
            self.add = f"Vaman Nivas Room No {self.r_no}, {str(self.flr_no).capitalize()}, Near Shree Pad Darshan front of Holy Cross English School, Nandivali Kalyan E. Maharashtra 421306."

        if self.build_name == BuildingCodes.ABHISHEK_APT:
            self.add = f"Abhishek Apartment Room No {self.r_no}, {str(self.flr_no).capitalize()}, Near Vedang Lake City behind, Nandivali Talav, Nandivali Kalyan E. Maharashtra 421306."
        super().save(*args, **kwargs)

    def __str__(self):
        return f"R-{self.r_code}"


class MeterDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    r_no = models.OneToOneField(RoomMaster, on_delete=models.CASCADE, related_name="meter_details", unique=True)
    meter_no = models.PositiveIntegerField(unique=True)
    bu_code = models.PositiveSmallIntegerField()
    con_type = models.CharField(max_length=12, default=ElectricityConsumer.LT)

    class Meta:
        db_table = "meter_details"
        managed = True

    def __str__(self):
        return self.meter_no


class RoomAllotment(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name="room_allotments", unique=True)
    r_no = models.OneToOneField(RoomMaster, on_delete=models.CASCADE, related_name="room_allotments", unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    agg_available = models.BooleanField(default=False)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "room_allotment"
        managed = True

    def save(self, *args, **kwargs):
        if self.start_date and not self.end_date:
            self.end_date = self.start_date + relativedelta(months=11, days=-1)
        super().save(*args, **kwargs)


class RentalDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    deposit = models.FloatField()
    rent = models.FloatField()
    maintenance = models.FloatField()
    rent_total = models.FloatField(default=0)
    rm_map = models.ForeignKey(RoomAllotment, on_delete=models.CASCADE, related_name="rental_details", unique=True)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rental_details"
        managed = True

    def save(self, *args, **kwargs):
        if self.rent and self.maintenance:
            self.rent_total = float(self.rent + self.maintenance)
        super().save(*args, **kwargs)


class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    tnx_no = models.CharField(max_length=20, unique=True)
    rm_map = models.ForeignKey(RoomAllotment, on_delete=models.CASCADE, related_name="transactions")
    amount = models.FloatField()
    is_rent = models.BooleanField(default=False)
    payment_mode = models.CharField(max_length=30, choices=PaymentModeChoices.choices, default=PaymentModeChoices.CASH)
    comment = models.CharField(max_length=255, null=True, blank=True)
    receipt = models.FileField(
        upload_to="receipts/",
        null=True,
        blank=True
    )
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transaction"
        managed = True

    def save(self, *args, **kwargs):
        _time = now()
        self.tnx_no = (
            f"TXN_{self.rm_map.r_no.r_code}_"
            f"{_time.strftime('%d%m%Y%H%M%S')}_"
            f"{random.randint(1000, 9999)}"
        )
        super().save(*args, **kwargs)


class Notice(models.Model):
    id = models.BigAutoField(primary_key=True)
    rm_map = models.ForeignKey(RoomAllotment, on_delete=models.CASCADE, related_name="notice")
    code = models.CharField(max_length=20, choices=NoticeType.choices, default=NoticeType.OTHER)
    desc = models.CharField(max_length=255, null=True, blank=True)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notice"
        managed = True
