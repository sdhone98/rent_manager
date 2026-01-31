import threading
from django.db import transaction
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from resources.generate_transaction_pdf import generate_transaction_html
from resources.send_transaction_email import (
    send_transaction_email,
    send_de_allotment_email,
    send_tnx_email_in_bg
)
from worker.models import (
    RoomMaster,
    RoomAllotment,
    Person,
    Address,
    Docs,
    RentalDetails,
    Transaction,
    Contact,
    RoomAllotmentExtra
)
from worker.serializer import (
    RoomMasterSerializer,
    PersonSerializer,
    AddressSerializer,
    DocsSerializer,
    RoomAllotmentSerializer,
    TransactionsSerializer,
    ContactSerializer,
    RentalDetailsSerializer,
    RoomAllotmentByRoomNumberSerializer,
    RoomAllotmentExtraSerializer
)
from worker.tasks import send_transaction_email_task


class RoomMasterAPIView(
    generics.ListCreateAPIView,
    generics.ListAPIView,
    generics.RetrieveUpdateDestroyAPIView,
):
    serializer_class = RoomMasterSerializer

    def get_queryset(self):
        queryset = RoomMaster.objects.all()
        room_id = self.kwargs.get("pk", False)
        building_code = self.request.query_params.get("building_code", False)

        if building_code:
            queryset = queryset.filter(
                build_name=building_code
            )
        if room_id:
            queryset = queryset.filter(id=self.kwargs['pk'])

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()


class RoomMasterDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView,
):
    serializer_class = RoomMasterSerializer

    def get_queryset(self):
        queryset = RoomMaster.objects.filter(id=self.kwargs['pk'])
        building_code = self.request.query_params.get("building_code", False)

        if building_code:
            queryset = queryset.filter(
                build_name=building_code
            )

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()


class AvailableRoomsView(
    generics.ListAPIView
):
    serializer_class = RoomMasterSerializer

    def get_queryset(self):
        building_code = self.request.query_params.get("building_code", False)

        queryset = RoomMaster.objects.all()

        active_rooms = RoomAllotment.objects.filter(
            is_active=True
        ).distinct()

        if active_rooms:
            queryset = queryset.exclude(
                id__in=active_rooms.values_list("room_id", flat=True)
            )

        if building_code:
            queryset = queryset.filter(build_name=building_code)

        return queryset


class PersonAPIView(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView,
):
    serializer_class = PersonSerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk", False)
        queryset = Person.objects.all()

        if pk:
            queryset = queryset.filter(pk=pk)

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()


class ContactByPersonAPIView(
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = ContactSerializer
    lookup_field = "person_id"

    def get_queryset(self):
        return Contact.objects.all()

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(person_id=self.kwargs["person_id"])


class AddressByPersonAPIView(
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = AddressSerializer
    lookup_field = "person_id"

    def get_queryset(self):
        return Address.objects.all()

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(person_id=self.kwargs["person_id"])


class DocumentsByPersonAPIView(
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView,
    generics.ListAPIView
):
    serializer_class = DocsSerializer
    lookup_field = "person_id"
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return Docs.objects.all()

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(person_id=self.kwargs["person_id"])


class RentalDetailsByRoomAllotmentAPIView(
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = RentalDetailsSerializer
    lookup_field = "rm_map"

    def get_queryset(self):
        return RentalDetails.objects.filter(rm_map=self.kwargs["rm_map"])

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(rm_map_id=self.kwargs["rm_map"])


class RoomAllotmentExtraSerializerByRoomAllotmentAPIView(
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = RoomAllotmentExtraSerializer
    lookup_field = "rm_map"

    def get_queryset(self):
        return RoomAllotmentExtra.objects.filter(
            rm_map=self.kwargs["rm_map"]
        )

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(rm_map_id=self.kwargs["rm_map"])


class ListAllRentalDetailsByPersonAPIView(
    generics.ListAPIView
):
    serializer_class = RentalDetailsSerializer
    lookup_field = "rm_map__person_id"

    def get_queryset(self):
        return RentalDetails.objects.filter(rm_map__person_id=self.kwargs["person_id"])


class RoomAllotmentByPersonAPIView(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView,
):
    serializer_class = RoomAllotmentSerializer
    lookup_field = "person_id"

    def get_queryset(self):
        return RoomAllotment.objects.filter(
            person_id=self.kwargs["person_id"],
        )

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(person_id=self.kwargs["person_id"])


class RoomAllotmentByRoomNumberAPIView(
    generics.RetrieveAPIView
):
    serializer_class = RoomAllotmentByRoomNumberSerializer
    lookup_field = "room__r_no"

    def get_queryset(self):
        building_code = self.request.query_params.get("building_code", False)

        if not building_code:
            raise ValidationError({
                "building_code": "This query parameter is required."
            })

        return RoomAllotment.objects.filter(
            is_active=True,
            room__r_no=self.kwargs["room__r_no"],
            room__build_name=building_code,
        )


class RoomDeAllotmentByPersonAPIView(
    generics.UpdateAPIView,
    generics.ListAPIView,
):
    serializer_class = RoomAllotmentSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return RoomAllotment.objects.filter(
            id=self.kwargs["pk"]
        )

    @transaction.atomic
    def perform_update(self, serializer):
        instance = serializer.save(
            is_active=False,
            actual_end_date=self.request.data.get("actual_end_date", timezone.now().date())
        )

        # SEND DE ALLOTMENT EMAIL WITH DETAILS
        send_de_allotment_email(instance)


class TransactionsByPersonAPIView(
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = TransactionsSerializer
    lookup_field = "rm_map"

    def get_queryset(self):
        return Transaction.objects.filter(
            rm_map__person_id=self.kwargs["person_id"],
            rm_map_id=self.kwargs["rm_map"]
        )

    @transaction.atomic
    def perform_create(self, serializer):
        transaction_instance = serializer.save(rm_map_id=self.kwargs["rm_map"])

        threading.Thread(
            target=send_tnx_email_in_bg,
            args=(transaction_instance.id,),
            daemon=True
        ).start()



class ListAllTransactionsByPersonAPIView(
    generics.ListAPIView
):
    serializer_class = TransactionsSerializer
    lookup_field = "person_id"

    def get_queryset(self):
        return Transaction.objects.filter(
            rm_map__person_id=self.kwargs["person_id"]
        )


class TransactionsAPIView(
    generics.ListAPIView
):
    serializer_class = TransactionsSerializer

    def get_queryset(self):
        return Transaction.objects.all()
