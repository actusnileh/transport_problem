from fastapi import APIRouter
from src.routes.solve_problem import router as solve_router

routes = APIRouter()

router_list = [solve_router]

for router in router_list:
    routes.include_router(router)
