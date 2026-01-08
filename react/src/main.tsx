import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { createBrowserRouter, Outlet, RouterProvider } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { ItemDetails } from './ItemDetails.tsx';
import { ItemSearch } from './ItemSearch.tsx';

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <>
        <main>
          <Outlet />
        </main>
      </>
    ),
    children: [
      {
        path: "/",
        element: <App />,
      },
      {
        path: "/search",
        element: <>
          <ItemSearch />
        </>
      },
      {
        path: "/item/:item_id",
        element: <>
          <ItemDetails />
        </>
      },
    ]
  }
]);


const query_client = new QueryClient();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={query_client}>
      <RouterProvider router={router} />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </StrictMode>,
)