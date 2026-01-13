from django.db import models


class BuildingCodes(models.TextChoices):
    VAMAN_NIVAS = "Vaman_Nivas", "VAMAN_NIVAS"
    ABHISHEK_APT = "Abhishek_Apartment", "ABHISHEK_APT"


class FloorCodes(models.TextChoices):
    GROUND = "Ground Floor", "GROUND"
    FIRST = "First Floor", "FIRST"
    SECOND = "Second Floor", "SECOND"
    THIRD = "Third Floor", "THIRD"
    FOURTH = "Fourth Floor", "FOURTH"


class RoleChoices(models.TextChoices):
    TENANT = "Tenant", "TENANT"
    OWNER = "Owner", "OWNER"
    MANAGER = "Manager", "MANAGER"


class PaymentModeChoices(models.TextChoices):
    CASH = "Cash", "CASH"
    UPI = "UPI", "UPI"
    BANK_TRANSFER = "Bank Transfer", "BANK_TRANSFER"
    CHEQUE = "Cheque", "CHEQUE"


from django.db import models


class StateCode(models.TextChoices):
    ANDHRA_PRADESH = "Andhra Pradesh", "ANDHRA_PRADESH"
    ARUNACHAL_PRADESH = "Arunachal Pradesh", "ARUNACHAL_PRADESH"
    ASSAM = "Assam", "ASSAM"
    BIHAR = "Bihar", "BIHAR"
    CHHATTISGARH = "Chhattisgarh", "CHHATTISGARH"
    GOA = "Goa", "GOA"
    GUJARAT = "Gujarat", "GUJARAT"
    HARYANA = "Haryana", "HARYANA"
    HIMACHAL_PRADESH = "Himachal Pradesh", "HIMACHAL_PRADESH"
    JHARKHAND = "Jharkhand", "JHARKHAND"
    KARNATAKA = "Karnataka", "KARNATAKA"
    KERALA = "Kerala", "KERALA"
    MADHYA_PRADESH = "Madhya Pradesh", "MADHYA_PRADESH"
    MAHARASHTRA = "Maharashtra", "MAHARASHTRA"
    MANIPUR = "Manipur", "MANIPUR"
    MEGHALAYA = "Meghalaya", "MEGHALAYA"
    MIZORAM = "Mizoram", "MIZORAM"
    NAGALAND = "Nagaland", "NAGALAND"
    ODISHA = "Odisha", "ODISHA"
    PUNJAB = "Punjab", "PUNJAB"
    RAJASTHAN = "Rajasthan", "RAJASTHAN"
    SIKKIM = "Sikkim", "SIKKIM"
    TAMIL_NADU = "Tamil Nadu", "TAMIL_NADU"
    TELANGANA = "Telangana", "TELANGANA"
    TRIPURA = "Tripura", "TRIPURA"
    UTTAR_PRADESH = "Uttar Pradesh", "UTTAR_PRADESH"
    UTTARAKHAND = "Uttarakhand", "UTTARAKHAND"
    WEST_BENGAL = "West Bengal", "WEST_BENGAL"

    ANDAMAN_NICOBAR = "Andaman and Nicobar Islands", "ANDAMAN_NICOBAR"
    CHANDIGARH = "Chandigarh", "CHANDIGARH"
    DADRA_NAGAR_HAVELI_DAMAN_DIU = (
        "Dadra & Nagar Haveli and Daman & Diu",
        "DADRA_NAGAR_HAVELI_DAMAN_DIU",
    )
    DELHI = "Delhi", "DELHI"
    JAMMU_KASHMIR = "Jammu and Kashmir", "JAMMU_KASHMIR"
    LADAKH = "Ladakh", "LADAKH"
    LAKSHADWEEP = "Lakshadweep", "LAKSHADWEEP"
    PUDUCHERRY = "Puducherry", "PUDUCHERRY"


class NoticeType(models.TextChoices):
    RENT_ALERT = "Rent Alert", "RENT_ALERT"
    RECEIPT_GEN = "Receipt Generation", "RECEIPT_GEN"
    NORMAL = "Normal", "NORMAL"
    OTHER = "Other", "OTHER"
