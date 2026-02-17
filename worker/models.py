import random
from django.db import models
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from resources.constant import ElectricityConsumer
from resources.custom_enums import (
    RoleChoices,
    StateCode,
    BuildingCodes,
    PaymentModeChoices,
    NoticeType,
    RoomLayout
)
from resources.person_doc_file_name_generator import (
    aadhaar_upload_path,
    pan_upload_path
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
    pn_code = models.TextField(max_length=6)

    class Meta:
        db_table = "address"
        managed = True


class Docs(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="docs", unique=True)
    aadhar_no = models.CharField(max_length=15, unique=True)
    aadhar_doc = models.FileField(upload_to=aadhaar_upload_path, null=True, blank=True)
    pan_no = models.CharField(max_length=255, unique=True)
    pan_doc = models.FileField(upload_to=pan_upload_path, null=True, blank=True)

    class Meta:
        db_table = "docs"
        managed = True


class RoomMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    r_no = models.IntegerField()
    flr_no = models.PositiveSmallIntegerField()
    add = models.CharField(max_length=255, null=True, blank=True)
    build_name = models.CharField(max_length=50, choices=BuildingCodes.choices)
    r_code = models.CharField(max_length=20, unique=True)
    code_name = models.CharField(max_length=20, unique=True)
    area = models.IntegerField(null=True, blank=True)
    layout = models.CharField(max_length=255, choices=RoomLayout.choices, null=True, blank=True)

    class Meta:
        db_table = "room_master"
        managed = True

    def save(self, *args, **kwargs):
        # Always generate room code
        self.r_code = f"{self.r_no}_{self.build_name}"
        self.code_name = f"{self.r_no}-{self.build_name}"

        # ADDRESS TEMPLATES PER BUILDING
        address_templates = {
            BuildingCodes.VAMAN_NIVAS: (
                "Vaman Nivas Room No {room}, Floor No {floor}, "
                "Near Shree Pad Darshan front of Holy Cross English School, "
                "Nandivali Kalyan E. Maharashtra 421306."
            ),
            BuildingCodes.ABHISHEK_APT: (
                "Abhishek Apartment Room No {room}, Floor No {floor}, "
                "Near Vedang Lake City behind, Nandivali Talav, "
                "Nandivali Kalyan E. Maharashtra 421306."
            ),
        }

        # AUTO-GENERATE ADDRESS ONLY IF NOT MANUALLY PROVIDED
        if not self.add and self.build_name in address_templates:
            self.add = address_templates[self.build_name].format(
                room=self.r_no,
                floor=str(self.flr_no).capitalize(),
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"R-{self.r_code}"

    def room_size(self):
        return f"{self.area} sq.ft."

    @property
    def status(self):
        return self.room_allotments.filter(is_active=True).exists()


class MeterDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    r_no = models.OneToOneField(RoomMaster, on_delete=models.CASCADE, related_name="meter_details", unique=True)
    meter_no = models.CharField(unique=True, max_length=12)
    bu_code = models.PositiveSmallIntegerField()
    con_type = models.CharField(max_length=12, default=ElectricityConsumer.LT)

    class Meta:
        db_table = "meter_details"
        managed = True

    def __str__(self):
        return self.meter_no


class RoomAllotment(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="room_allotments")
    room = models.ForeignKey(RoomMaster, on_delete=models.CASCADE, related_name="room_allotments")
    start_date = models.DateField()
    end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "room_allotment"
        managed = True
        indexes = [
            models.Index(fields=["room", "is_active"]),
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if self.start_date and not self.end_date:
            self.end_date = self.start_date + relativedelta(months=11, days=-1)

            # ROOM ALLOTTED
            self.is_active = True

        super().save(*args, **kwargs)

        if is_new:
            RoomAllotmentExtra.objects.get_or_create(rm_map=self)


class RoomAllotmentExtra(models.Model):
    id = models.BigAutoField(primary_key=True)
    rm_map = models.OneToOneField(
        RoomAllotment,
        on_delete=models.CASCADE,
        related_name="extra",
        editable=False,
    )
    agg_available = models.BooleanField(default=False)
    is_painted = models.BooleanField(default=False)
    is_water_tank = models.BooleanField(default=False)
    is_grill = models.BooleanField(default=False)
    is_ele_bill_clear = models.BooleanField(default=False)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "room_allotment_related_details"
        managed = True


class RentalDetails(models.Model):
    id = models.BigAutoField(primary_key=True)
    deposit = models.IntegerField()
    rent = models.IntegerField()
    maintenance = models.IntegerField()
    rent_total = models.IntegerField(default=0)
    rm_map = models.ForeignKey(RoomAllotment, on_delete=models.CASCADE, related_name="rental_details", unique=True)
    ts = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rental_details"
        managed = True

    def save(self, *args, **kwargs):
        if self.rent and self.maintenance:
            self.rent_total = self.rent + self.maintenance
        super().save(*args, **kwargs)


class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    tnx_no = models.CharField(max_length=20, unique=True)
    rm_map = models.ForeignKey(RoomAllotment, on_delete=models.CASCADE, related_name="transactions")
    amount = models.IntegerField()
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
        self.tnx_no = (
            f"TXN_{now().strftime('%d%m%Y%H%M%S')}"
            f"_{get_building_code(self.rm_map.room.build_name)}"
            f"_{self.rm_map.room.r_no}"
            f"_{random.randint(1000, 9999)}"
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


def get_building_code(_building_name):
    if _building_name == BuildingCodes.ABHISHEK_APT:
        return "A"
    elif _building_name == BuildingCodes.VAMAN_NIVAS:
        return "V"
    else:
        return "O"
