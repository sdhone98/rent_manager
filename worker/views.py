import threading
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from resources.send_transaction_email import (
    send_de_allotment_email,
    send_tnx_email_in_bg,
    send_de_allotment_email_in_bg
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
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView,
):
    serializer_class = PersonSerializer

    def get_queryset(self):
        queryset = Person.objects.all()

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()


class PersonsAPIView(
    generics.ListAPIView,
):
    serializer_class = PersonSerializer

    def get_queryset(self):
        queryset = Person.objects.all()

        return queryset


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


class RoomAllotmentByBuildingNameAPIView(
    generics.ListAPIView,
):
    serializer_class = RoomAllotmentByRoomNumberSerializer

    def get_queryset(self):
        building_code = self.request.query_params.get("building_code", False)

        if not building_code:
            raise ValidationError({
                "building_code": "This query parameter is required."
            })

        return RoomAllotment.objects.filter(
            is_active=True,
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

        threading.Thread(
            target=send_de_allotment_email_in_bg,
            args=(instance.id,),
            daemon=True
        ).start()

        # SEND DE ALLOTMENT EMAIL WITH DETAILS
        send_de_allotment_email(instance)


class TransactionsByPersonAPIView(
    generics.ListAPIView,
    generics.CreateAPIView,
    generics.RetrieveUpdateDestroyAPIView,
):
    serializer_class = TransactionsSerializer
    lookup_field = "rm_map"

    def get_queryset(self):
        return Transaction.objects.filter(
            # rm_map__person_id=self.kwargs["person_id"],
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
        transactions_type = self.request.query_params.get("transactions_type", False)
        if transactions_type and transactions_type == "all":
            return Transaction.objects.all()
        else:
            return Transaction.objects.filter(rm_map__is_active=True).all()


class BuildingRoomStatsView(APIView):
    """
    Returns building-wise room statistics:
    - total rooms
    - occupied rooms
    - vacant rooms
    """

    def get(self, request):
        queryset = (
            RoomMaster.objects
            .values("build_name")
            .annotate(
                total_rooms=Count("id"),
                occupied_rooms=Count(
                    "room_allotments",
                    filter=Q(room_allotments__is_active=True),
                    distinct=True
                )
            )
            .order_by("build_name")
        )

        data = []
        for item in queryset:
            data.append({
                "building": item["build_name"],
                "total_rooms": item["total_rooms"],
                "occupied_rooms": item["occupied_rooms"],
                "vacant_rooms": item["total_rooms"] - item["occupied_rooms"],
            })

        queryset_1 = (
            RoomMaster.objects
            .values("layout")
            .annotate(
                total_rooms=Count("id"),
                vacant_rooms=Count(
                    "id",
                    filter=~Q(room_allotments__is_active=True),
                    distinct=True
                )
            )
            .order_by("layout")
        )

        return Response(
            {"test": queryset_1, "test_1": data},
            status=status.HTTP_200_OK
        )
