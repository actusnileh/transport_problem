import axios from "axios";
import React, { useState } from "react";
import {
    NumberInput,
    Button,
    Grid,
    Container,
    Table,
    Title,
    Paper,
    Space,
    Divider,
} from "@mantine/core";

import "./text.css";

export const HomePage = () => {
    const [suppliers, setSuppliers] = useState(1);
    const [consumers, setConsumers] = useState(1);
    const [costMatrix, setCostMatrix] = useState([]);
    const [orders, setOrders] = useState([]);
    const [inventory, setInventory] = useState([]);
    const [showMatrix, setShowMatrix] = useState(false);
    const [solutionResult, setSolutionResult] = useState("");
    const [allocation, setAllocation] = useState([]);
    const [totalCost, setTotalCost] = useState(0);
    const [iterations, setIterations] = useState([]);

    const handleCalculate = () => {
        const matrix = Array.from({ length: suppliers }, () =>
            Array(consumers).fill(0)
        );
        setCostMatrix(matrix);
        setOrders(Array(consumers).fill());
        setInventory(Array(suppliers).fill());
        setShowMatrix(true);
    };

    const handleCostChange = (value, supplierIndex, consumerIndex) => {
        const newMatrix = costMatrix.map((row, i) =>
            row.map((cost, j) =>
                i === supplierIndex && j === consumerIndex ? value : cost
            )
        );
        setCostMatrix(newMatrix);
    };

    const handleInventoryChange = (value, index) => {
        const newInventory = [...inventory];
        newInventory[index] = value;
        setInventory(newInventory);
    };

    const handleOrderChange = (value, index) => {
        const newOrders = [...orders];
        newOrders[index] = value;
        setOrders(newOrders);
    };

    const handleSolveProblem = async () => {
        try {
            const response = await axios.post(
                "http://0.0.0.0:8000/solve_problem/",
                {
                    orders,
                    inventory,
                    cost_matrix: costMatrix,
                }
            );

            const result = response.data;
            console.log("Результат первого запроса:", result);
            setIterations(result.iterations);
            setAllocation(result.iterations[result.iterations.length - 1].plan);
            setTotalCost(result.iterations[result.iterations.length - 1].cost);

            // Теперь выполняем второй запрос
            await handleSolveAdditionalProblem();
        } catch (error) {
            console.error("Ошибка при решении задачи:", error);
            if (error.response) {
                console.error("Ответ от сервера:", error.response.data);
            }
        }
    };

    const handleSolveAdditionalProblem = async () => {
        try {
            const response = await axios.post(
                "http://0.0.0.0:8000/solve_problem_str/",
                {
                    orders,
                    inventory,
                    cost_matrix: costMatrix,
                }
            );

            const result = response.data;
            console.log("Результат второго запроса:", result);
            setSolutionResult(result);
        } catch (error) {
            console.error("Ошибка при решении дополнительной задачи:", error);
            if (error.response) {
                console.error("Ответ от сервера:", error.response.data);
            }
        }
    };

    const handleBack = () => {
        setShowMatrix(false);
        setCostMatrix([]);
        setOrders([]);
        setInventory([]);
        setAllocation([]);
        setIterations([]);
        setTotalCost(0);
    };

    // Функция для автоматического заполнения значений
    const handleAutoFill = () => {
        setOrders([20, 15, 25, 20]);
        setInventory([30, 25, 20]);
        setCostMatrix([
            [4, 5, 3, 6],
            [7, 2, 1, 5],
            [6, 1, 4, 2],
        ]);
    };

    return (
        <Container style={{ textAlign: "center", padding: "2rem" }}>
            <Paper shadow="xl" radius="xl" p={"md"} bg={"#262626"}>
                <Title order={1}>Транспортная задача</Title>
                <Space h="md" />
                {!showMatrix ? (
                    <>
                        <Grid mt="xl" justify="center">
                            <Grid.Col span={5}>
                                <NumberInput
                                    label="Количество потребителей"
                                    value={consumers}
                                    onChange={setConsumers}
                                    min={1}
                                    max={10}
                                    required
                                    styles={{ input: { textAlign: "center" } }}
                                />
                            </Grid.Col>
                            <Grid.Col span={5}>
                                <NumberInput
                                    label="Количество поставщиков"
                                    value={suppliers}
                                    onChange={setSuppliers}
                                    min={1}
                                    max={10}
                                    required
                                    styles={{
                                        input: { textAlign: "center" },
                                    }}
                                />
                            </Grid.Col>
                        </Grid>

                        <Button mt="lg" onClick={handleCalculate} color="blue">
                            Далее
                        </Button>
                    </>
                ) : (
                    <div style={{ marginTop: "20px" }}>
                        <Table withColumnBorders>
                            <Table.Thead>
                                <Table.Tr>
                                    <Table.Th>Запасы(A) / Заказы(B)</Table.Th>
                                    {orders.map((_, index) => (
                                        <Table.Th key={index}>
                                            <NumberInput
                                                value={orders[index]}
                                                onChange={(value) =>
                                                    handleOrderChange(
                                                        value,
                                                        index
                                                    )
                                                }
                                                placeholder={`B(${index + 1})`}
                                                hideControls
                                                styles={{
                                                    input: {
                                                        textAlign: "center",
                                                    },
                                                }}
                                            />
                                        </Table.Th>
                                    ))}
                                </Table.Tr>
                            </Table.Thead>
                            <Table.Tbody>
                                {costMatrix.map((row, supplierIndex) => (
                                    <Table.Tr key={supplierIndex}>
                                        <Table.Td>
                                            <NumberInput
                                                value={inventory[supplierIndex]}
                                                onChange={(value) =>
                                                    handleInventoryChange(
                                                        value,
                                                        supplierIndex
                                                    )
                                                }
                                                placeholder={`A(${
                                                    supplierIndex + 1
                                                })`}
                                                hideControls
                                                styles={{
                                                    input: {
                                                        textAlign: "center",
                                                    },
                                                }}
                                            />
                                        </Table.Td>
                                        {row.map((cost, consumerIndex) => (
                                            <Table.Td key={consumerIndex}>
                                                <NumberInput
                                                    value={cost}
                                                    onChange={(value) =>
                                                        handleCostChange(
                                                            value,
                                                            supplierIndex,
                                                            consumerIndex
                                                        )
                                                    }
                                                    min={0}
                                                    styles={{
                                                        input: {
                                                            textAlign: "center",
                                                        },
                                                    }}
                                                />
                                            </Table.Td>
                                        ))}
                                    </Table.Tr>
                                ))}
                            </Table.Tbody>
                        </Table>
                        <Container mb="md" mt="md">
                            <Button
                                onClick={handleBack}
                                mr={"md"}
                                variant="default"
                            >
                                Назад
                            </Button>
                            <Button onClick={handleSolveProblem} color="blue">
                                Решить задачу
                            </Button>
                            <Button
                                onClick={handleAutoFill}
                                color="green"
                                ml="md"
                            >
                                Заполнить автоматически
                            </Button>
                        </Container>
                    </div>
                )}
                {(iterations.length > 0 || solutionResult) && (
                    <div style={{ marginTop: "20px" }}>
                        {iterations.length > 0 && (
                            <div>
                                {iterations.map((iteration, index) => (
                                    <div key={index}>
                                        <Divider my={"md"} />
                                        <Title order={4}>
                                            Итерация {index + 1}
                                        </Title>
                                        <Table
                                            highlightOnHover
                                            withColumnBorders
                                        >
                                            <Table.Thead>
                                                <Table.Tr>
                                                    <Table.Th></Table.Th>
                                                    {orders.map(
                                                        (order, index) => (
                                                            <Table.Th
                                                                key={index}
                                                            >
                                                                <div
                                                                    style={{
                                                                        textAlign:
                                                                            "center",
                                                                    }}
                                                                >
                                                                    {order || 0}
                                                                </div>
                                                            </Table.Th>
                                                        )
                                                    )}
                                                </Table.Tr>
                                            </Table.Thead>
                                            <Table.Tbody>
                                                {iteration.plan.map(
                                                    (row, supplierIndex) => (
                                                        <Table.Tr
                                                            key={supplierIndex}
                                                        >
                                                            <Table.Td>
                                                                <div
                                                                    style={{
                                                                        textAlign:
                                                                            "center",
                                                                    }}
                                                                >
                                                                    {
                                                                        inventory[
                                                                            supplierIndex
                                                                        ]
                                                                    }
                                                                </div>
                                                            </Table.Td>
                                                            {row.map(
                                                                (
                                                                    value,
                                                                    consumerIndex
                                                                ) => (
                                                                    <Table.Td
                                                                        key={
                                                                            consumerIndex
                                                                        }
                                                                    >
                                                                        <div
                                                                            style={{
                                                                                textAlign:
                                                                                    "center",
                                                                            }}
                                                                        >
                                                                            {
                                                                                value
                                                                            }
                                                                        </div>
                                                                    </Table.Td>
                                                                )
                                                            )}
                                                        </Table.Tr>
                                                    )
                                                )}
                                            </Table.Tbody>
                                        </Table>
                                        <Title order={5}>
                                            Затраты: {iteration.cost}
                                        </Title>
                                    </div>
                                ))}
                                <Divider my={"xl"} />
                                {solutionResult && (
                                    <div
                                        className="gradient-text"
                                        style={{
                                            marginTop: "20px",
                                            padding: "10px",
                                            border: "1px solid #ccc",
                                            borderRadius: "5px",
                                        }}
                                    >
                                        <Title order={4} mb={"md"}>
                                            Текстовое решение:
                                        </Title>
                                        <div
                                            style={{
                                                whiteSpace: "pre-line",
                                                fontFamily: "monospace",
                                            }}
                                        >
                                            {solutionResult}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </Paper>
        </Container>
    );
};
