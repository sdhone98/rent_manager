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
        fields = "__all__"
        extra_kwargs = {
            "person_id": {
                "required": False
            }
        }

    def validate(self, attrs):
        person_id = self.context["view"].kwargs.get("person_id")
        validation_person(person_id)
        return attrs


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        extra_kwargs = {
            "person_id": {
                "required": False
            }
        }

    def validate(self, attrs):
        validation_person(attrs["person_id"])
        return attrs


class DocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docs
        fields = "__all__"
        extra_kwargs = {
            "person_id": {
                "required": False
            }
        }

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
        person_id = self.context["view"].kwargs.get("person_id")
        validation_person(person_id)
        return attrs


class RoomAllotmentSerializer(serializers.ModelSerializer):
    end_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = RoomAllotment
        fields = "__all__"
        extra_kwargs = {
            "person_id": {
                "required": False
            }
        }

    def validate(self, attrs):
        person_id = self.context["view"].kwargs.get("person_id")
        validation_person(person_id)
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

    def validate(self, attrs):
        person_id = self.context["view"].kwargs.get("person_id")
        validation_person(person_id)
        return attrs


class TransactionsSerializer(serializers.ModelSerializer):
    tnx_no = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Transaction
        fields = "__all__"
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
