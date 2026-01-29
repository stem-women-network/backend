from fastapi import APIRouter
from src.controllers.meeting_controller import (
    MeetingController,
    MeetingResponse,
    MeetingCreate,
    MeetingUpdate,
    UpcomingMeetingResponse,
    UpcomingMeetingCreate,
    UpcomingMeetingUpdate,
)
from src.database import SessionDep

router = APIRouter()



@router.get("/", response_model=list[MeetingResponse])
def list_meetings(session: SessionDep):
    return MeetingController.list_meetings(session)


@router.get("/{id_encontro}", response_model=MeetingResponse)
def get_meeting(id_encontro: int, session: SessionDep):
    return MeetingController.get_meeting(id_encontro, session)


@router.post("/", response_model=MeetingResponse)
def create_meeting(data: MeetingCreate, session: SessionDep):
    return MeetingController.create_meeting(data, session)


@router.put("/{id_encontro}", response_model=MeetingResponse)
def update_meeting(id_encontro: int, data: MeetingUpdate, session: SessionDep):
    return MeetingController.update_meeting(id_encontro, data, session)


@router.delete("/{id_encontro}")
def delete_meeting(id_encontro: int, session: SessionDep):
    return MeetingController.delete_meeting(id_encontro, session)





@router.get("/upcoming", response_model=list[UpcomingMeetingResponse])
def list_upcoming_meetings(session: SessionDep):
    return MeetingController.list_upcoming_meetings(session)


@router.get("/upcoming/{id_proximo_encontro}", response_model=UpcomingMeetingResponse)
def get_upcoming_meeting(id_proximo_encontro: int, session: SessionDep):
    return MeetingController.get_upcoming_meeting(id_proximo_encontro, session)


@router.post("/upcoming", response_model=UpcomingMeetingResponse)
def create_upcoming_meeting(data: UpcomingMeetingCreate, session: SessionDep):
    return MeetingController.create_upcoming_meeting(data, session)


@router.put("/upcoming/{id_proximo_encontro}", response_model=UpcomingMeetingResponse)
def update_upcoming_meeting(id_proximo_encontro: int, data: UpcomingMeetingUpdate, session: SessionDep):
    return MeetingController.update_upcoming_meeting(id_proximo_encontro, data, session)


@router.delete("/upcoming/{id_proximo_encontro}")
def delete_upcoming_meeting(id_proximo_encontro: int, session: SessionDep):
    return MeetingController.delete_upcoming_meeting(id_proximo_encontro, session)