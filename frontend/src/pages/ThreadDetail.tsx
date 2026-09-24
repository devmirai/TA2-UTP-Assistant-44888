import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button, Spin, Typography } from 'antd';
import { Attachments, Bubble, Sender } from '@ant-design/x';
import { getThread, type ChatMsg, type ThreadDetailData } from '../api/threads';
import { RunChain } from '../components/RunChain';

const { Title, Text } = Typography;

export function ThreadDetailPage(): JSX.Element {
  const { id = '' } = useParams();
  const navigate = useNavigate();
  const [thread, setThread] = useState<ThreadDetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [draft, setDraft] = useState('');

  useEffect(() => {
    let alive = true;
    setLoading(true);
    getThread(id)
      .then((t) => {
        if (!alive) return;
        setThread(t);
        setMessages(t?.messages ?? []);
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, [id]);

  if (loading) {
    return (
      <div style={{ padding: 24 }}>
        <Spin />
      </div>
    );
  }

  if (!thread) {
    return (
      <div style={{ padding: 24 }}>
        <Text>Hilo no encontrado.</Text>
        <div style={{ marginTop: 12 }}>
          <Button onClick={() => navigate('/inbox')}>Volver a inbox</Button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 760, margin: '0 auto', padding: 24 }}>
      <Button onClick={() => navigate('/inbox')} style={{ marginBottom: 16 }}>
        Volver a inbox
      </Button>
      <Title level={4} style={{ marginBottom: 4 }}>
        {thread.subject}
      </Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>
        {thread.contactFullName} · {thread.company} · módulo {thread.module}
      </Text>

      <Bubble.List
        items={messages.map((m) => ({ key: m.key, role: m.role, content: m.content }))}
        role={{
          user: { placement: 'end' },
          assistant: { placement: 'start' },
        }}
        style={{ marginBottom: 16 }}
      />

      <RunChain threadId={id} runId="run_ana_001" />

      <div style={{ marginBottom: 16 }}>
        <Text strong style={{ display: 'block', marginBottom: 8 }}>
          Adjuntos
        </Text>
        <Attachments
          items={thread.attachments.map((a, i) => ({ uid: `att-${i}`, name: a.name }))}
        />
      </div>

      <Sender
        value={draft}
        onChange={setDraft}
        placeholder="Responder a Ana Torres…"
        onSubmit={(msg) => {
          const text = msg.trim();
          if (!text) return;
          setMessages((prev) => [...prev, { key: `local-${Date.now()}`, role: 'user', content: text }]);
          setDraft('');
        }}
      />
    </div>
  );
}

export default ThreadDetailPage;
