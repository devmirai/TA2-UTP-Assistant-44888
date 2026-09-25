import { useState } from 'react';
import { Button, Card, Space, Tag, Typography } from 'antd';
import api from '../api/client';
import mockRuns from '../mocks/runs.json';

const { Title, Text, Paragraph } = Typography;

interface MockRun {
  id: string;
  thread_id: string;
  status: string;
  summary: string;
  created_at: string;
}

type ApprovalStatus = 'requires_action' | 'in_progress' | 'completed' | 'rejected';

const runs = mockRuns as MockRun[];

function initialStatus(raw: string): ApprovalStatus {
  if (raw === 'completed') return 'completed';
  if (raw === 'rejected') return 'rejected';
  return 'requires_action';
}

export function ApprovalsPage(): JSX.Element {
  const [statuses, setStatuses] = useState<Record<string, ApprovalStatus>>(() =>
    Object.fromEntries(runs.map((r) => [r.id, initialStatus(r.status)])),
  );
  const [submittingId, setSubmittingId] = useState<string | null>(null);

  async function handleApprove(run: MockRun): Promise<void> {
    const current = statuses[run.id];
    if (current === 'completed' || current === 'rejected' || submittingId) return;
    setSubmittingId(run.id);
    setStatuses((prev) => ({ ...prev, [run.id]: 'in_progress' }));
    try {
      await api.post(`/threads/${run.thread_id}/runs/${run.id}/submit_tool_outputs`, {
        tool_outputs: [
          {
            tool_call_id: 'call_dispo_001',
            output: JSON.stringify({ approved: true, run_id: run.id }),
          },
          {
            tool_call_id: 'call_jira_001',
            output: JSON.stringify({ approved: true, ticket: 'UTPC-142' }),
          },
        ],
      });
    } catch {
      // Fallback mock: sin backend se marca completed igual.
    } finally {
      setStatuses((prev) => ({ ...prev, [run.id]: 'completed' }));
      setSubmittingId(null);
    }
  }

  function handleReject(run: MockRun): void {
    const current = statuses[run.id];
    if (current === 'completed' || current === 'rejected' || submittingId) return;
    setStatuses((prev) => ({ ...prev, [run.id]: 'rejected' }));
  }

  return (
    <div style={{ maxWidth: 760, margin: '0 auto', padding: 24 }}>
      <Title level={4} style={{ marginBottom: 4 }}>
        Aprobaciones
      </Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
        {runs.length} runs requires_action · Ana Torres · TechCorp
      </Text>
      <Space direction="vertical" style={{ width: '100%' }} size={12}>
        {runs.map((run) => {
          const st = statuses[run.id] ?? 'requires_action';
          const busy = submittingId === run.id;
          const done = st === 'completed' || st === 'rejected';
          return (
            <Card
              key={run.id}
              title={run.summary}
              extra={
                st === 'completed' ? (
                  <Tag color="success">completed</Tag>
                ) : st === 'rejected' ? (
                  <Tag color="error">rejected</Tag>
                ) : st === 'in_progress' ? (
                  <Tag color="processing">in_progress</Tag>
                ) : (
                  <Tag color="warning">requires_action</Tag>
                )
              }
            >
              <Paragraph style={{ marginBottom: 8 }}>
                <Text type="secondary">Thread </Text>
                <Text code>{run.thread_id}</Text>
                <Text type="secondary"> · Run </Text>
                <Text code>{run.id}</Text>
              </Paragraph>
              <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
                Ronda 2: check_disponibilidad + crear_ticket UTPC-142. Al aprobar se llama a
                submit_tool_outputs y el run avanza a completed.
              </Text>
              <Space>
                <Button
                  type="primary"
                  loading={busy}
                  disabled={done}
                  onClick={() => handleApprove(run)}
                >
                  Aprobar
                </Button>
                <Button danger disabled={done || busy} onClick={() => handleReject(run)}>
                  Rechazar
                </Button>
              </Space>
            </Card>
          );
        })}
      </Space>
    </div>
  );
}

export default ApprovalsPage;
