import { useState } from 'react';
import { Button, Space, Tag, Typography } from 'antd';
import { ThoughtChain } from '@ant-design/x';
import api from '../api/client';

const { Text, Paragraph } = Typography;

interface RunChainProps {
  threadId?: string;
  runId?: string;
  onApproved?: (runId: string) => void;
  onRejected?: (runId: string) => void;
}

type ChainStatus = 'requires_action' | 'in_progress' | 'completed' | 'rejected';

const ROUND1_ENTITIES = {
  empresa: 'TechCorp',
  contacto: 'Ana Torres',
  email: 'ana@techcorp.example',
  tema: 'módulo pagos',
  compromiso: 'reunión próxima semana',
  adjunto: true,
  adjunto_nombre: 'req_inicial.pdf',
};

const ROUND2_TOOLS = {
  check_disponibilidad: {
    args: { asistentes: ['ana@techcorp.example'], duracion_minutos: 60 },
    slots: ['2026-09-30T15:00:00Z', '2026-10-01T16:00:00Z'],
  },
  crear_ticket: {
    proyecto: 'UTPC',
    key: 'UTPC-142',
    titulo: '[TechCorp] Revisar requisitos módulo pagos',
    estado: 'To Do',
  },
};

export function RunChain({
  threadId = 'th_ana_001',
  runId = 'run_ana_001',
  onApproved,
  onRejected,
}: RunChainProps): JSX.Element {
  const [status, setStatus] = useState<ChainStatus>('requires_action');
  const [submitting, setSubmitting] = useState(false);

  const done = status === 'completed' || status === 'rejected';
  const round2Status = status === 'completed' ? 'success' : status === 'rejected' ? 'error' : 'loading';

  async function handleApprove(): Promise<void> {
    if (done || submitting) return;
    setSubmitting(true);
    setStatus('in_progress');
    try {
      await api.post(`/threads/${threadId}/runs/${runId}/submit_tool_outputs`, {
        tool_outputs: [
          {
            tool_call_id: 'call_dispo_001',
            output: JSON.stringify({ approved: true, slots: ROUND2_TOOLS.check_disponibilidad.slots }),
          },
          {
            tool_call_id: 'call_jira_001',
            output: JSON.stringify({ approved: true, ticket: ROUND2_TOOLS.crear_ticket.key }),
          },
        ],
      });
    } catch {
      // Fallback mock: sin backend, se avanza igual a completed.
    } finally {
      setStatus('completed');
      setSubmitting(false);
      onApproved?.(runId);
    }
  }

  function handleReject(): void {
    if (done || submitting) return;
    setStatus('rejected');
    onRejected?.(runId);
  }

  return (
    <div style={{ marginTop: 16 }}>
      <Space style={{ marginBottom: 8 }}>
        <Text strong>Run {runId}</Text>
        {status === 'completed' ? (
          <Tag color="success">completed</Tag>
        ) : status === 'rejected' ? (
          <Tag color="error">rejected</Tag>
        ) : status === 'in_progress' ? (
          <Tag color="processing">in_progress</Tag>
        ) : (
          <Tag color="warning">requires_action</Tag>
        )}
      </Space>
      <ThoughtChain
        defaultExpandedKeys={['round-1', 'round-2']}
        items={[
          {
            key: 'round-1',
            title: 'Ronda 1 — Extraer + parse adjunto',
            description: 'extract_entities · parse_adjunto → requires_action resuelto',
            content: (
              <Paragraph style={{ margin: 0 }}>
                <Text type="secondary">Entidades extraídas de req_inicial.pdf:</Text>
                <pre style={{ margin: '8px 0 0', fontSize: 12, whiteSpace: 'pre-wrap' }}>
                  {JSON.stringify(ROUND1_ENTITIES, null, 2)}
                </pre>
              </Paragraph>
            ),
            status: 'success',
            collapsible: true,
          },
          {
            key: 'round-2',
            title: 'Ronda 2 — Disponibilidad + Jira UTPC-142',
            description: 'check_disponibilidad · crear_ticket UTPC-142 → requiere aprobación',
            content: (
              <div>
                <Text type="secondary">Slots devueltos por tool:</Text>
                <ul style={{ margin: '4px 0 8px', paddingLeft: 18 }}>
                  {ROUND2_TOOLS.check_disponibilidad.slots.map((s) => (
                    <li key={s}>
                      <Text code>{s}</Text>
                    </li>
                  ))}
                </ul>
                <Text type="secondary">Ticket:</Text>{' '}
                <Text code>UTPC-142</Text> <Text type="secondary">— {ROUND2_TOOLS.crear_ticket.titulo}</Text>
                {status === 'completed' && (
                  <div style={{ marginTop: 8 }}>
                    <Tag color="success">completed</Tag>
                    <Text type="secondary"> Respuesta interna lista, pendiente confirmación humana.</Text>
                  </div>
                )}
                {status === 'rejected' && (
                  <div style={{ marginTop: 8 }}>
                    <Tag color="error">rejected</Tag>
                  </div>
                )}
              </div>
            ),
            footer: (
              <Space>
                <Button type="primary" size="small" loading={submitting} disabled={done} onClick={handleApprove}>
                  Aprobar
                </Button>
                <Button size="small" danger disabled={done || submitting} onClick={handleReject}>
                  Rechazar
                </Button>
              </Space>
            ),
            status: round2Status,
            collapsible: true,
          },
        ]}
      />
    </div>
  );
}

export default RunChain;
