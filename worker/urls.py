from django.urls import path
from worker.views import (
    AvailableRoomsView,
    AddressByPersonAPIView,
    DocumentsByPersonAPIView,
    RentalDetailsByPersonAPIView,
    RoomAllotmentByPersonAPIView,
    TransactionsByPersonAPIView,
    ContactByPersonAPIView,
    RoomMasterAPIView,
    PersonAPIView,
    ListAllTransactionsByPersonAPIView,
    ListAllRentalDetailsByPersonAPIView,
    RoomDeAllotmentByPersonAPIView,
    RoomMasterDetailAPIView
)

urlpatterns = [
    path("room/", RoomMasterAPIView.as_view(), name="room-list-create"),
    path("room/", RoomMasterAPIView.as_view(), name="room-detail"),
    path("room/<int:pk>/", RoomMasterDetailAPIView.as_view(), name="room-detail"),

    path("room/available/", AvailableRoomsView.as_view(), name="available-rooms"),

    path("person/", PersonAPIView.as_view(), name="person-list-create"),
    path("person/<int:pk>/", PersonAPIView.as_view(), name="person-detail"),

    path("person/<int:person_id>/contact/", ContactByPersonAPIView.as_view(), name="contact"),

    path("person/<int:person_id>/address/", AddressByPersonAPIView.as_view(), name="address"),

    path("person/<int:person_id>/doc/", DocumentsByPersonAPIView.as_view(), name="documents"),

    path("person/<int:person_id>/room-allotment/", RoomAllotmentByPersonAPIView.as_view(), name="room-allotment"),
    path("room-de-allotment/<int:pk>/", RoomDeAllotmentByPersonAPIView.as_view(), name="room-de-allotment"),

    path("room-allotment/<int:rm_map>/rental-details/", RentalDetailsByPersonAPIView.as_view(), name="rental-details"),
    path("person/<int:person_id>/rental-details/", ListAllRentalDetailsByPersonAPIView.as_view(),
         name="rental-details"),

    path("room-allotment/<int:rm_map>/transactions/", TransactionsByPersonAPIView.as_view(), name="transactions"),
    path("person/<int:person_id>/transactions/", ListAllTransactionsByPersonAPIView.as_view(), name="transactions"),

]
