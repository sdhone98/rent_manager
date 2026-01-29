from django.db import models


class BuildingCodes(models.TextChoices):
    VAMAN_NIVAS = "Vaman Nivas"
    ABHISHEK_APT = "Abhishek Apartment"


class FloorCodes:
    GROUND = 1
    FIRST = 2
    SECOND = 3
    THIRD = 4
    FOURTH = 5

    CHOICES = (
        (GROUND, GROUND),
        (FIRST, FIRST),
        (SECOND, SECOND),
        (THIRD, THIRD),
        (FOURTH, FOURTH),
    )


class RoomLayout(models.TextChoices):
    ONE_RK = "1RK"
    ONE_BHK = "1BHK"
    TWO_BHK = "2BHK"


class RoleChoices(models.TextChoices):
    TENANT = "Tenant"
    OWNER = "Owner"
    MANAGER = "Manager"


class PaymentModeChoices(models.TextChoices):
    CASH = "Cash"
    UPI = "UPI"
    BANK_TRANSFER = "Bank Transfer"
    CHEQUE = "Cheque"


class StateCode(models.TextChoices):
    ANDHRA_PRADESH = "Andhra Pradesh"
    ARUNACHAL_PRADESH = "Arunachal Pradesh"
    ASSAM = "Assam"
    BIHAR = "Bihar"
    CHHATTISGARH = "Chhattisgarh"
    GOA = "Goa"
    GUJARAT = "Gujarat"
    HARYANA = "Haryana"
    HIMACHAL_PRADESH = "Himachal Pradesh"
    JHARKHAND = "Jharkhand"
    KARNATAKA = "Karnataka"
    KERALA = "Kerala"
    MADHYA_PRADESH = "Madhya Pradesh"
    MAHARASHTRA = "Maharashtra"
    MANIPUR = "Manipur"
    MEGHALAYA = "Meghalaya"
    MIZORAM = "Mizoram"
    NAGALAND = "Nagaland"
    ODISHA = "Odisha"
    PUNJAB = "Punjab"
    RAJASTHAN = "Rajasthan"
    SIKKIM = "Sikkim"
    TAMIL_NADU = "Tamil Nadu"
    TELANGANA = "Telangana"
    TRIPURA = "Tripura"
    UTTAR_PRADESH = "Uttar Pradesh"
    UTTARAKHAND = "Uttarakhand"
    WEST_BENGAL = "West Bengal"

    ANDAMAN_NICOBAR = "Andaman and Nicobar Islands"
    CHANDIGARH = "Chandigarh"
    DADRA_NAGAR_HAVELI_DAMAN_DIU = "Dadra & Nagar Haveli and Daman & Diu"
    DELHI = "Delhi"
    JAMMU_KASHMIR = "Jammu and Kashmir"
    LADAKH = "Ladakh"
    LAKSHADWEEP = "Lakshadweep"
    PUDUCHERRY = "Puducherry"


class NoticeType(models.TextChoices):
    RENT_ALERT = "Rent Alert"
    RECEIPT_GEN = "Receipt Generation"
    NORMAL = "Normal"
    OTHER = "Other"
