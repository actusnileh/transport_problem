from fastapi import APIRouter

import numpy as np

from src.schemas.transport_schema import (
    TransportIterationResponse,
    TransportRequest,
    TransportResponse,
)
from src.services.transport_service import (
    TransportData,
    find_cycle_path,
    is_degenerate_plan,
    make_start_plan_non_degenerate,
    recalculate_plan,
)


router = APIRouter()


@router.post("/solve_problem/", response_model=TransportResponse)
async def solve_problem(data: TransportRequest):
    transport_data = TransportData(data.orders, data.inventory, data.cost_matrix)

    difference = transport_data.get_orders_inventory_difference()
    iterations = []

    if difference > 0:
        transport_data.add_dummy_inventory(difference)
    elif difference < 0:
        transport_data.add_dummy_order(-difference)

    plan = transport_data.get_plan_by_north_west_method()

    while True:
        cost = transport_data.calculate_cost(plan)
        potentials = transport_data.calculate_potentials(plan)

        plan_cleaned = np.nan_to_num(plan, nan=0.0).tolist()

        iterations.append(
            TransportIterationResponse(
                iteration=len(iterations) + 1,
                plan=plan_cleaned,
                cost=cost,
                potentials=potentials,
            )
        )

        optimal = transport_data.is_plan_optimal(plan, potentials)

        if optimal:
            break

        cycle_path = find_cycle_path(
            plan, transport_data.get_best_free_cell(plan, potentials)
        )

        recalculate_plan(plan, cycle_path)

        if is_degenerate_plan(plan):
            make_start_plan_non_degenerate(plan)

    return TransportResponse(iterations=iterations)


@router.post("/solve_problem_str/", response_model=str)
async def solve_problem_str(data: TransportRequest):
    transport_data = TransportData(data.orders, data.inventory, data.cost_matrix)
    result = []

    # Разница между спросом и предложением
    difference = transport_data.get_orders_inventory_difference()
    result.append(f"Разница между спросом и предложением: {difference}")

    if difference > 0:
        result.append("Не хватает предложения.")
        transport_data.add_dummy_inventory(difference)
        result.append(f"Добавлен фиктивный поставщик с объемом {difference}.")
    elif difference < 0:
        result.append("Не хватает спроса.")
        transport_data.add_dummy_order(-difference)
        result.append(f"Добавлен фиктивный потребитель с объемом {-difference}.")

    # Начальный опорный план
    plan = transport_data.get_plan_by_north_west_method()
    result.append("Начальный опорный план методом северо-западного угла:")
    result.append("\n".join(["\t".join(map(str, row)) for row in plan]))

    # Проверка на вырожденность
    if is_degenerate_plan(plan):
        make_start_plan_non_degenerate(plan)

    # Итеративный процесс
    while True:
        first_cost = transport_data.calculate_cost(plan)
        result.append(f"\nСтоимость: {first_cost:.2f}")

        # Потенциалы
        potentials = transport_data.calculate_potentials(plan)
        result.append("\nПотенциалы:")
        result.append(f"u: {[float(x) for x in potentials['a']]}\n")
        result.append(f"v: {[float(x) for x in potentials['b']]}\n")

        # Проверка оптимальности
        if transport_data.is_plan_optimal(plan, potentials):
            result.append("\nПлан оптимален: Да")
            break
        else:
            result.append("\nПлан оптимален: Нет")

        # Циклический путь и пересчет плана
        cycle_path = find_cycle_path(
            plan, transport_data.get_best_free_cell(plan, potentials)
        )
        result.append(
            f"Циклический путь: {[tuple(float(y) for y in x) for x in cycle_path]}\n"
        )

        o = recalculate_plan(plan, cycle_path)
        result.append(f"\nПересчет плана с величиной o: {o:.2f}")

        # Новый план
        result.append("Новый план:")
        result.append("\n".join(["\t".join(map(str, row)) for row in plan]))

    # Финальный вывод
    return "\n".join(result)
