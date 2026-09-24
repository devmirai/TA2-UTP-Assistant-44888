import { createBrowserRouter, Navigate } from 'react-router-dom';
import { InboxPage } from './pages/Inbox';
import { ThreadDetailPage } from './pages/ThreadDetail';
import { ApprovalsPage } from './pages/Approvals';
import { BoardPage } from './pages/Board';

export const router = createBrowserRouter([
  { path: '/', element: <Navigate to="/inbox" replace /> },
  { path: '/inbox', element: <InboxPage /> },
  { path: '/thread/:id', element: <ThreadDetailPage /> },
  { path: '/approvals', element: <ApprovalsPage /> },
  { path: '/board', element: <BoardPage /> },
]);

export default router;
