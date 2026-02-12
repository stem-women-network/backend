from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, Response
from starlette.status import HTTP_401_UNAUTHORIZED
from src.controllers.admin_controller import AdminController, UpdateApproval, UpdateApprovalMentee
from src.database import SessionDep


router = APIRouter()

@router.get("/get-approvals")
def get_approvals(request : Request, response : Response, session: SessionDep):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        mentors = AdminController.get_approvals(token, session)
        return mentors
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

@router.post("/update-approval")
def update_approval(data : UpdateApproval, request : Request, response : Response, session: SessionDep):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        AdminController.update_approval(data,token, session)
        return []
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

@router.get("/get-approvals-mentee")
def get_approvals_mentee(request : Request, response : Response, session: SessionDep):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        mentees = AdminController.get_approvals_mentee(token, session)
        return mentees
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

@router.post("/update-approval-mentee")
def update_approval_mentee(data : UpdateApprovalMentee, request : Request, response : Response, session: SessionDep):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        AdminController.update_approval_mentee(data,token, session)
        return []
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
