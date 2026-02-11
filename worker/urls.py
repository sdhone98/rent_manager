from django.urls import path
from worker.views import (
    AvailableRoomsView,
    AddressByPersonAPIView,
    DocumentsByPersonAPIView,
    RoomAllotmentByPersonAPIView,
    TransactionsByPersonAPIView,
    ContactByPersonAPIView,
    RoomMasterAPIView,
    PersonAPIView,
    ListAllTransactionsByPersonAPIView,
    ListAllRentalDetailsByPersonAPIView,
    RoomDeAllotmentByPersonAPIView,
    RoomMasterDetailAPIView,
    RoomAllotmentByRoomNumberAPIView,
    TransactionsAPIView,
    RentalDetailsByRoomAllotmentAPIView,
    RoomAllotmentExtraSerializerByRoomAllotmentAPIView,
    PersonsAPIView,
    BuildingRoomStatsView,
    RoomAllotmentByBuildingNameAPIView,
    RoomAllotmentExpiryAPIView
)

urlpatterns = [
    path("room/", RoomMasterAPIView.as_view(), name="room-detail"),
    path("room/<int:pk>/", RoomMasterDetailAPIView.as_view(), name="room-detail"),

    path("room/available/", AvailableRoomsView.as_view(), name="available-rooms"),

    path("person/", PersonsAPIView.as_view(), name="person-list-create"),
    path("person/<int:pk>/", PersonAPIView.as_view(), name="person-detail"),

    path("person/<int:person_id>/contact/", ContactByPersonAPIView.as_view(), name="contact"),

    path("person/<int:person_id>/address/", AddressByPersonAPIView.as_view(), name="address"),

    path("person/<int:person_id>/doc/", DocumentsByPersonAPIView.as_view(), name="documents"),

    path("person/<int:person_id>/room-allotment/", RoomAllotmentByPersonAPIView.as_view(), name="room-allotment"),
    path("room-allotment/<int:room__r_no>/", RoomAllotmentByRoomNumberAPIView.as_view(), name="room-allotment"),
    path("room-allotment/", RoomAllotmentByBuildingNameAPIView.as_view(), name="room-allotment-by-building"),
    path("room-allotment/expiry/", RoomAllotmentExpiryAPIView.as_view(), name="room-allotment-expiry"),
    path("room-de-allotment/<int:pk>/", RoomDeAllotmentByPersonAPIView.as_view(), name="room-de-allotment"),

    path("room-allotment/<int:rm_map>/rental-details/",
         RentalDetailsByRoomAllotmentAPIView.as_view(),
         name="rental-details"),
    path("room-allotment/<int:rm_map>/rental-related-details/",
         RoomAllotmentExtraSerializerByRoomAllotmentAPIView.as_view(),
         name="rental-related-details"),
    path("person/<int:person_id>/rental-details/",
         ListAllRentalDetailsByPersonAPIView.as_view(),
         name="rental-details"),

    path("room-allotment/<int:rm_map>/transactions/", TransactionsByPersonAPIView.as_view(), name="transactions"),
    path("person/<int:person_id>/transactions/", ListAllTransactionsByPersonAPIView.as_view(), name="transactions"),
    path("transactions/", TransactionsAPIView.as_view(), name="all-transactions"),

    path("home/", BuildingRoomStatsView.as_view(), name="room-list-create"),
]
