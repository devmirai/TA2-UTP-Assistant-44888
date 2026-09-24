import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider } from 'antd';
import { XProvider } from '@ant-design/x';
import { RouterProvider } from 'react-router-dom';
import { router } from './router';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ConfigProvider>
      <XProvider>
        <RouterProvider router={router} />
      </XProvider>
    </ConfigProvider>
  </React.StrictMode>,
);
