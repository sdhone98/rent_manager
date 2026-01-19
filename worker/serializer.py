import re

from rest_framework import serializers
from worker.models import RoomMaster, Person, Address, Docs, RoomAllotment, Transaction, Contact, RentalDetails


class RoomMasterSerializer(serializers.ModelSerializer):
    r_code = serializers.CharField(required=False)

    class Meta:
        model = RoomMaster
        fields = "__all__"


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        exclude = ("person",)

    def validate(self, attrs):
        person_id = self.context["view"].kwargs.get("person_id")

        # PREVENT DUPLICATE CONTACT
        if self.instance is None and Contact.objects.filter(person_id=person_id).exists():
            raise serializers.ValidationError("Person contact details already exist")

        validation_person(person_id)
        return attrs


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ("person",)

    def validate(self, attrs):
        person_id = self.context["view"].kwargs.get("person_id")

        # PREVENT DUPLICATE CONTACT
        if self.instance is None and Address.objects.filter(person_id=person_id).exists():
            raise serializers.ValidationError("Person address details already exist")
        validation_person(person_id)
        return attrs


class DocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docs
        exclude = ("person",)

    def validate_aadhaar_doc(self, file):
        self._validate_pdf(file, field_name="Aadhaar document")
        return file

    def validate_pan_doc(self, file):
        self._validate_pdf(file, field_name="PAN document")
        return file

    def _validate_pdf(self, file, field_name):
        if not file.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                f"{field_name} must be a PDF file."
            )

        if file.content_type != "application/pdf":
            raise serializers.ValidationError(
                f"{field_name} must be a valid PDF."
            )

        max_size = 5 * 1024 * 1024
        if file.size > max_size:
            raise serializers.ValidationError(
                f"{field_name} size must be less than 5MB."
            )

    def validate(self, attrs):
        # AADHAR NO SHOULD NE 12 CHAR
        if attrs.get("aadhar_no"):
            if len(attrs["aadhar_no"]) != 12:
                raise serializers.ValidationError("Aadhar number must be 12 digits.")

        # VALIDATE PAN NO
        if attrs.get("pan_no"):
            validate_pan(attrs["pan_no"])

        person_id = self.context["view"].kwargs.get("person_id")

        # PREVENT DUPLICATE CONTACT
        if self.instance is None and Docs.objects.filter(person_id=person_id).exists():
            raise serializers.ValidationError("Person documents already exist")
        validation_person(person_id)
        return attrs


class RoomAllotmentSerializer(serializers.ModelSerializer):
    end_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = RoomAllotment
        exclude = ("person",)

    def validate(self, attrs):
        request = self.context.get("request")

        # CHECK ROOM OCCUPIED OR NOT ( WHILE CREATING )
        if request and request.method == "POST":
            person_id = self.context["view"].kwargs.get("person_id")

            if RoomAllotment.objects.filter(
                    room_id=attrs["room"],
                    is_active=True
            ).exists():
                raise serializers.ValidationError("Room already occupied!")

            validation_person(person_id)

        # CHECK ROOM OCCUPIED OR NOT ( WHILE CREATING )
        if request and request.method == "PATCH":
            pk = self.context["view"].kwargs.get("pk")
            if RoomAllotment.objects.filter(
                    id=pk,
                    is_active=False
            ).exists():
                raise serializers.ValidationError("Room already De Activated.!")

        return attrs


class RentalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalDetails
        fields = "__all__"
        extra_kwargs = {
            "rm_map": {
                "required": False
            }
        }


class TransactionsSerializer(serializers.ModelSerializer):
    tnx_no = serializers.CharField(required=False, allow_blank=True)
    room = serializers.IntegerField(
        source="rm_map.room.r_no",
        read_only=True
    )
    building_name = serializers.CharField(
        source="rm_map.room.build_name",
        read_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "tnx_no",
            "amount",
            "is_rent",
            "payment_mode",
            "comment",
            "receipt",
            "ts",
            "rm_map",
            "room",
            "building_name",
        ]
        extra_kwargs = {
            "rm_map": {
                "required": False
            }
        }

    def validate(self, attrs):
        rm_map = self.context["view"].kwargs.get("rm_map")

        validation_room_allotment(rm_map)
        validation_amount(attrs["amount"])
        return attrs


def validation_person(value):
    if not Person.objects.filter(id=value).exists():
        raise serializers.ValidationError("Person does not exist")
    return value


def validation_room_allotment(value):
    if not RoomAllotment.objects.filter(id=value).exists():
        raise serializers.ValidationError("RoomAllotment does not exist")


def validation_amount(value):
    if value < 0:
        raise serializers.ValidationError("Amount must be greater than zero.")
    return value


def validate_pan(pan: str) -> bool | None:
    if not pan:
        return False

    pan = pan.upper()

    pattern = (
        r'^[A-Z]{3}'  # First 3 alphabets
        r'[PCFHATBLJG]'  # 4th char - Entity type
        r'[A-Z]'  # 5th char - Surname initial
        r'[0-9]{4}'  # Next 4 digits
        r'[A-Z]$'  # Last char - checksum
    )

    if not bool(re.match(pattern, pan)):
        raise serializers.ValidationError("Invalid PAN number.")
    return None
