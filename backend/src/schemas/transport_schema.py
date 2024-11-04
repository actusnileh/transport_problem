from pydantic import BaseModel


class TransportRequest(BaseModel):
    orders: list[int]
    inventory: list[int]
    cost_matrix: list[list[int]]


class TransportIterationResponse(BaseModel):
    iteration: int
    plan: list[list[float]]
    cost: float
    potentials: dict[str, list[float]]


class TransportResponse(BaseModel):
    iterations: list[TransportIterationResponse]
