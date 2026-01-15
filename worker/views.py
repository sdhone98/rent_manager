from django.db import transaction
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from resources.generate_transaction_pdf import generate_transaction_html
from resources.send_transaction_email import send_transaction_email
from worker.models import (
    RoomMaster,
    RoomAllotment,
    Person,
    Address,
    Docs,
    RentalDetails,
    Transaction,
    Contact
)
from worker.serializer import (
    RoomMasterSerializer,
    PersonSerializer,
    AddressSerializer,
    DocsSerializer,
    RoomAllotmentSerializer,
    TransactionsSerializer,
    ContactSerializer,
    RentalDetailsSerializer
)


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


class AvailableRoomsView(
    generics.ListAPIView
):
    serializer_class = RoomMasterSerializer

    def get_queryset(self):
        building_code = self.request.query_params.get("building_code", False)

        queryset = RoomMaster.objects.all()

        active_rooms = RoomAllotment.objects.filter(
            is_active=False
        ).distinct()

        if active_rooms:
            queryset = queryset.filter(
                id__in=active_rooms
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
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = DocsSerializer
    lookup_field = "person_id"
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return Docs.objects.all()

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(person_id=self.kwargs["person_id"])


class RentalDetailsByPersonAPIView(
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


class ListAllRentalDetailsByPersonAPIView(
    generics.ListAPIView
):
    serializer_class = RentalDetailsSerializer
    lookup_field = "rm_map__person_id"

    def get_queryset(self):
        return RentalDetails.objects.filter(rm_map__person_id=self.kwargs["person_id"])


class RoomAllotmentByPersonAPIView(
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView
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

        # GENERATE TRANSACTION PDF
        file_name = generate_transaction_html(transaction_instance)

        # Save receipt path
        transaction_instance.receipt = f"{file_name}"
        transaction_instance.save(update_fields=["receipt"])

        send_transaction_email(transaction)
        # send_whatsapp_receipt(transaction)


class ListAllTransactionsByPersonAPIView(
    generics.ListAPIView
):
    serializer_class = TransactionsSerializer
    lookup_field = "person_id"

    def get_queryset(self):
        return Transaction.objects.filter(
            rm_map__person_id=self.kwargs["person_id"]
        )
