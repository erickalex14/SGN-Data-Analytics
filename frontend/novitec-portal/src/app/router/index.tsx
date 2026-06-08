import { lazy, Suspense, type ReactNode } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { PortalLayout } from "@/app/layouts/portal-layout";
import { RouteLoadingFallback } from "@/shared/ui/feedback/route-loading-fallback";

const LoginPage = lazy(() =>
  import("@/features/auth/pages/login-page").then((module) => ({
    default: module.LoginPage,
  })),
);
const ExecutiveDashboardPage = lazy(() =>
  import("@/features/executive/pages/executive-dashboard-page").then((module) => ({
    default: module.ExecutiveDashboardPage,
  })),
);
const OperationalPage = lazy(() =>
  import("@/features/operational/pages/operational-page").then((module) => ({
    default: module.OperationalPage,
  })),
);
const FinancialPage = lazy(() =>
  import("@/features/financial/pages/financial-page").then((module) => ({
    default: module.FinancialPage,
  })),
);
const TechnicalPage = lazy(() =>
  import("@/features/technical/pages/technical-page").then((module) => ({
    default: module.TechnicalPage,
  })),
);
const InventoryPage = lazy(() =>
  import("@/features/inventory/pages/inventory-page").then((module) => ({
    default: module.InventoryPage,
  })),
);
const CrmPage = lazy(() =>
  import("@/features/crm/pages/crm-page").then((module) => ({
    default: module.CrmPage,
  })),
);
const WarrantyPage = lazy(() =>
  import("@/features/warranty/pages/warranty-page").then((module) => ({
    default: module.WarrantyPage,
  })),
);
const OrganizationalPage = lazy(() =>
  import("@/features/organizational/pages/organizational-page").then((module) => ({
    default: module.OrganizationalPage,
  })),
);
const ExportsCenterPage = lazy(() =>
  import("@/features/exports/pages/exports-center-page").then((module) => ({
    default: module.ExportsCenterPage,
  })),
);

// Envuelve cada ruta diferida para mantener una experiencia uniforme de carga.
function withSuspense(element: ReactNode) {
  return <Suspense fallback={<RouteLoadingFallback />}>{element}</Suspense>;
}

// Define las rutas principales del portal ejecutivo.
const router = createBrowserRouter([
  {
    path: "/login",
    element: withSuspense(<LoginPage />),
  },
  {
    path: "/",
    element: <PortalLayout />,
    children: [
      {
        index: true,
        element: withSuspense(<ExecutiveDashboardPage />),
      },
      {
        path: "operaciones",
        element: withSuspense(<OperationalPage />),
      },
      {
        path: "financiero",
        element: withSuspense(<FinancialPage />),
      },
      {
        path: "tecnico",
        element: withSuspense(<TechnicalPage />),
      },
      {
        path: "inventario",
        element: withSuspense(<InventoryPage />),
      },
      {
        path: "crm",
        element: withSuspense(<CrmPage />),
      },
      {
        path: "garantias",
        element: withSuspense(<WarrantyPage />),
      },
      {
        path: "organizacional",
        element: withSuspense(<OrganizationalPage />),
      },
      {
        path: "exportes",
        element: withSuspense(<ExportsCenterPage />),
      },
    ],
  },
]);

// Expone el proveedor de rutas de la aplicacion.
export function AppRouter() {
  return <RouterProvider router={router} />;
}
