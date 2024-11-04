import numpy as np


class TransportData:
    def __init__(
        self,
        orders: list[int],
        inventory: list[int],
        cost_matrix: list[list[int]],
    ) -> None:
        self.orders = np.array(orders)
        self.inventory = np.array(inventory)
        self.cost_matrix = np.array(cost_matrix)
        self.count_inventory = len(inventory)
        self.count_orders = len(orders)

    def get_orders_inventory_difference(self) -> int:
        return np.sum(self.orders) - np.sum(self.inventory)

    def calculate_cost(self, plan: np.ndarray) -> float:
        return np.sum(self.cost_matrix * np.nan_to_num(plan))

    def add_dummy_inventory(self, volume: int) -> None:
        e = np.zeros(self.count_orders)
        self.cost_matrix = np.vstack((self.cost_matrix, e))
        self.inventory = np.append(self.inventory, volume)
        self.count_inventory += 1

    def add_dummy_order(self, volume: int) -> None:
        e = np.zeros(self.count_inventory)
        self.cost_matrix = np.column_stack((self.cost_matrix, e))
        self.orders = np.append(self.orders, volume)
        self.count_orders += 1

    def get_plan_by_north_west_method(self) -> np.ndarray:
        start_plan = np.zeros((self.count_inventory, self.count_orders))

        orders = self.orders.copy()
        inventory = self.inventory.copy()
        i, j = 0, 0

        while i < self.count_inventory and j < self.count_orders:
            x = min(inventory[i], orders[j])
            inventory[i] -= x
            orders[j] -= x

            start_plan[i][j] = x

            if inventory[i] == 0:
                i += 1

            if orders[j] == 0:
                j += 1

        return start_plan

    def calculate_potentials(self, x: np.ndarray) -> dict[str, np.ndarray]:
        """Вычисление потенциалов."""
        res = {
            "a": [np.inf for _ in range(self.count_inventory)],
            "b": [np.inf for _ in range(self.count_orders)],
        }
        res["a"][0] = 0.0

        while np.inf in res["a"] or np.inf in res["b"]:
            for i in range(self.count_inventory):
                for j in range(self.count_orders):
                    if x[i][j] != 0:
                        if res["a"][i] != np.inf:
                            res["b"][j] = self.cost_matrix[i][j] - res["a"][i]
                        elif res["b"][j] != np.inf:
                            res["a"][i] = self.cost_matrix[i][j] - res["b"][j]

        return res

    def is_plan_optimal(self, x: np.ndarray, p: dict[str, np.ndarray]) -> bool:
        for i, j in zip(*np.nonzero(x == 0)):
            if p["a"][i] + p["b"][j] > self.cost_matrix[i][j]:
                return False
        return True

    def get_best_free_cell(
        self, x: np.ndarray, p: dict[str, np.ndarray]
    ) -> tuple[int, int]:
        free_cells = tuple(zip(*np.nonzero(x == 0)))
        return free_cells[
            np.argmax(
                [p["a"][i] + p["b"][j] - self.cost_matrix[i][j] for i, j in free_cells]
            )
        ]


def find_cycle_path(x: np.ndarray, start_pos: tuple[int, int]) -> list[tuple[int, int]]:
    def get_posible_moves(
        bool_table: np.ndarray, path: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        posible_moves = np.full(bool_table.shape, False)

        current_pos = path[-1]
        prev_pos = path[-2] if len(path) > 1 else (np.nan, np.nan)

        if current_pos[0] != prev_pos[0]:
            posible_moves[current_pos[0]] = True

        if current_pos[1] != prev_pos[1]:
            posible_moves[:, current_pos[1]] = True

        return list(zip(*np.nonzero(posible_moves * bool_table)))

    res = [start_pos]
    bool_table = x != 0

    while True:
        current_pos = res[-1]
        bool_table[current_pos[0]][current_pos[1]] = False

        if len(res) > 3:
            bool_table[start_pos[0]][start_pos[1]] = True

        posible_moves = get_posible_moves(bool_table, res)

        if start_pos in posible_moves:
            res.append(start_pos)
            return res

        if not posible_moves:
            for i, j in res[1:-1]:
                bool_table[i][j] = True
            res = [start_pos]
            continue

        res.append(posible_moves[0])


def recalculate_plan(x: np.ndarray, cycle_path: list[tuple[int, int]]) -> int:
    """Пересчитать план. Возвращает величину пересчета."""
    o = np.min([x[i][j] for i, j in cycle_path[1:-1:2]])
    minus_cells_equal_to_o = [
        (i, j) for i, j in cycle_path[1:-1:2] if np.isnan(x[i][j]) or x[i][j] == o
    ]

    if np.isnan(o):
        i, j = cycle_path[0]
        x[i][j] = np.nan
        i, j = minus_cells_equal_to_o[0]
        x[i][j] = 0
        return o

    for k, (i, j) in enumerate(cycle_path[:-1]):
        if (i, j) in minus_cells_equal_to_o:
            if minus_cells_equal_to_o.index((i, j)) == 0:
                x[i][j] = 0
            else:
                x[i][j] = np.nan
            continue

        if np.isnan(x[i][j]):
            x[i][j] = 0

        if k % 2 == 0:
            x[i][j] += o
        else:
            x[i][j] -= o

    return o


def is_degenerate_plan(x: np.ndarray) -> bool:
    """Проверка плана на вырожденность."""
    m, n = x.shape
    return np.count_nonzero(x) != m + n - 1


def make_start_plan_non_degenerate(x: np.ndarray) -> None:
    m, n = x.shape

    while np.count_nonzero(x) != m + n - 1:
        for i in range(m):
            if np.count_nonzero(x[i]) == 1:
                j = np.nonzero(x[i])[0][0]

                if np.count_nonzero(x[:, j]) == 1:
                    if np.nonzero(x[:, j])[0][0] == i:
                        if i < m - 1:
                            x[i + 1][j] = np.nan
                        else:
                            x[i - 1][j] = np.nan

                        break
