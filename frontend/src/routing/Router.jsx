import { createBrowserRouter } from "react-router-dom";
import { HomePage } from "../pages/page";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <HomePage />,
    },
]);
