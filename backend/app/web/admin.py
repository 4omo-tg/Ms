from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Adjust path relative to where app runs usually (root of backend)
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# POIs
@router.get("/pois", response_class=HTMLResponse)
async def list_pois(request: Request):
    return templates.TemplateResponse("pois.html", {"request": request})

@router.get("/pois/new", response_class=HTMLResponse)
async def create_poi(request: Request):
    return templates.TemplateResponse("poi_form.html", {"request": request})

@router.get("/pois/{poi_id}", response_class=HTMLResponse)
async def edit_poi(request: Request, poi_id: int):
    return templates.TemplateResponse("poi_form.html", {"request": request})

# Routes
@router.get("/routes", response_class=HTMLResponse)
async def list_routes(request: Request):
    return templates.TemplateResponse("routes.html", {"request": request})

@router.get("/routes/new", response_class=HTMLResponse)
async def create_route(request: Request):
    return templates.TemplateResponse("route_form.html", {"request": request})

@router.get("/routes/{route_id}", response_class=HTMLResponse)
async def edit_route(request: Request, route_id: int):
    return templates.TemplateResponse("route_form.html", {"request": request})
