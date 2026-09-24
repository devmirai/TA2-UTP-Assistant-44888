import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Spin, Table, Typography } from 'antd';
import { Conversations } from '@ant-design/x';
import { getThreads, type ThreadSummary } from '../api/threads';
import { useAppStore } from '../store/useAppStore';

const { Title, Text } = Typography;

interface MailRow {
  key: string;
  from: string;
  subject: string;
  company: string;
  module: string;
  date: string;
  status: string;
}

const columns = [
  { title: 'De', dataIndex: 'from', key: 'from' },
  { title: 'Asunto', dataIndex: 'subject', key: 'subject' },
  { title: 'Empresa', dataIndex: 'company', key: 'company' },
  { title: 'Módulo', dataIndex: 'module', key: 'module' },
  { title: 'Fecha', dataIndex: 'date', key: 'date' },
  { title: 'Estado', dataIndex: 'status', key: 'status' },
];

export function InboxPage(): JSX.Element {
  const navigate = useNavigate();
  const { activeThread, setActiveThread } = useAppStore();
  const [threads, setThreads] = useState<ThreadSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    getThreads()
      .then((list) => {
        if (alive) setThreads(list);
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  const sorted = [...threads].sort((a, b) => +new Date(b.date) - +new Date(a.date));
  const items = sorted.map((t, i) => ({
    key: t.id,
    label: t.subject,
    group: i === 0 ? 'Hoy' : 'Ayer',
  }));

  const rows: MailRow[] = sorted.map((t) => ({
    key: t.id,
    from: 'Ana Torres <ana@techcorp.example>',
    subject: t.subject,
    company: 'TechCorp',
    module: 'pagos',
    date: t.date.slice(0, 10),
    status: t.status,
  }));

  return (
    <div style={{ display: 'flex', gap: 24, padding: 24, minHeight: '100vh' }}>
      <div style={{ width: 300, flexShrink: 0 }}>
        <Title level={4} style={{ marginBottom: 4 }}>
          Bandeja
        </Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 12 }}>
          {threads.length} hilos
        </Text>
        {loading ? (
          <Spin />
        ) : (
          <Conversations
            items={items}
            groupable
            activeKey={activeThread ?? undefined}
            onActiveChange={(key) => {
              setActiveThread(key);
              navigate(`/thread/${key}`);
            }}
          />
        )}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <Title level={4}>Correos — Ana Torres · TechCorp · módulo pagos</Title>
        <Table
          columns={columns}
          dataSource={rows}
          loading={loading}
          pagination={false}
          rowKey="key"
          onRow={(record) => ({
            onClick: () => {
              setActiveThread(record.key);
              navigate(`/thread/${record.key}`);
            },
            style: { cursor: 'pointer' },
          })}
        />
      </div>
    </div>
  );
}

export default InboxPage;
