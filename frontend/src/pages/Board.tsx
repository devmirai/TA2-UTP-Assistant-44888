import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Card, Space, Tag, Typography } from 'antd';
import { Prompts } from '@ant-design/x';
import rawTickets from '../mocks/jira.json';

const { Title, Text, Paragraph } = Typography;

type ColumnKey = 'todo' | 'doing' | 'done';

interface JiraTicket {
  key: string;
  summary?: string;
  title?: string;
  status?: string;
  assignee?: string;
  company?: string;
  module?: string;
  modulo?: string;
}

const TICKETS = rawTickets as JiraTicket[];

const UTPC_FALLBACK: JiraTicket = {
  key: 'UTPC-142',
  summary: '[TechCorp] Revisar requisitos módulo pagos',
  status: 'To Do',
  assignee: 'Ana',
  company: 'TechCorp',
  module: 'pagos',
};

function normalizeStatus(raw: string | undefined): ColumnKey {
  const s = (raw ?? '').toLowerCase().replace(/[\s_-]+/g, ' ').trim();
  if (s === 'to do' || s === 'todo' || s === 'to-do' || s === 'open' || s === 'por hacer') return 'todo';
  if (s === 'in progress' || s === 'doing' || s === 'inprogress' || s === 'en curso') return 'doing';
  return 'done';
}

function ticketModule(t: JiraTicket): string {
  return t.module ?? t.modulo ?? (t.company === 'TechCorp' ? 'pagos' : '—');
}

function ticketSummary(t: JiraTicket): string {
  return t.summary ?? t.title ?? t.key;
}

const COLUMNS: { key: ColumnKey; title: string; anchor: string; tagColor: string }[] = [
  { key: 'todo', title: 'To Do', anchor: 'col-todo', tagColor: 'default' },
  { key: 'doing', title: 'Doing', anchor: 'col-doing', tagColor: 'processing' },
  { key: 'done', title: 'Done', anchor: 'col-done', tagColor: 'success' },
];

const SHORTCUTS = [
  { key: 'go-todo', label: 'Ver To Do', description: 'Ir a la columna To Do' },
  { key: 'go-doing', label: 'Ver Doing', description: 'Ir a la columna Doing' },
  { key: 'go-done', label: 'Ver Done', description: 'Ir a la columna Done' },
  { key: 'go-utpc-142', label: 'Abrir UTPC-142', description: 'TechCorp · módulo pagos' },
];

export function BoardPage(): JSX.Element {
  const navigate = useNavigate();

  const tickets = useMemo<JiraTicket[]>(() => {
    const list = [...TICKETS];
    if (!list.some((t) => t.key === UTPC_FALLBACK.key)) list.unshift({ ...UTPC_FALLBACK });
    return list;
  }, []);

  const byColumn = useMemo<Record<ColumnKey, JiraTicket[]>>(
    () => ({
      todo: tickets.filter((t) => normalizeStatus(t.status) === 'todo'),
      doing: tickets.filter((t) => normalizeStatus(t.status) === 'doing'),
      done: tickets.filter((t) => normalizeStatus(t.status) === 'done'),
    }),
    [tickets],
  );

  function handleShortcut(key: string): void {
    const anchor = key === 'go-todo' ? 'col-todo' : key === 'go-doing' ? 'col-doing' : key === 'go-done' ? 'col-done' : null;
    if (anchor) {
      document.getElementById(anchor)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    if (key === 'go-utpc-142') {
      document.getElementById('ticket-UTPC-142')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: 24 }}>
      <Space style={{ marginBottom: 12 }}>
        <Button onClick={() => navigate('/inbox')}>Volver a inbox</Button>
        <Button onClick={() => navigate('/approvals')}>Ver aprobaciones</Button>
      </Space>

      <Title level={4} style={{ marginBottom: 4 }}>
        Tablero
      </Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
        {tickets.length} tickets · UTPC-142 en To Do · TechCorp · módulo pagos
      </Text>

      <div style={{ marginBottom: 16 }}>
        <Prompts items={SHORTCUTS} onItemClick={({ data }) => handleShortcut(data.key)} />
      </div>

      <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
        {COLUMNS.map((col) => {
          const items = byColumn[col.key];
          return (
            <section
              key={col.key}
              id={col.anchor}
              aria-label={col.title}
              style={{ flex: 1, minWidth: 0, scrollMarginTop: 16 }}
            >
              <Space style={{ marginBottom: 12 }} align="center">
                <Text strong>{col.title}</Text>
                <Tag color={col.tagColor}>{items.length}</Tag>
              </Space>
              <Space direction="vertical" style={{ width: '100%' }} size={12}>
                {items.map((t) => (
                  <Card
                    key={t.key}
                    id={`ticket-${t.key}`}
                    title={t.key}
                    extra={<Tag>{t.status ?? col.title}</Tag>}
                    style={{ scrollMarginTop: 16, scrollMarginBottom: 16 }}
                  >
                    <Paragraph style={{ marginBottom: 8 }}>{ticketSummary(t)}</Paragraph>
                    <Text type="secondary" style={{ display: 'block' }}>
                      Empresa: {t.company ?? '—'}
                    </Text>
                    <Text type="secondary" style={{ display: 'block' }}>
                      Módulo: {ticketModule(t)}
                    </Text>
                    {t.assignee && (
                      <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
                        Responsable: {t.assignee}
                      </Text>
                    )}
                  </Card>
                ))}
                {items.length === 0 && (
                  <Text type="secondary">Sin tickets en {col.title}.</Text>
                )}
              </Space>
            </section>
          );
        })}
      </div>
    </div>
  );
}

export default BoardPage;
