import api from './client';
import mockThreads from '../mocks/threads.json';

export interface ThreadSummary {
  id: string;
  subject: string;
  from: string;
  company: string;
  contact: string;
  snippet: string;
  date: string;
  status: string;
}

export interface ChatMsg {
  key: string | number;
  role: 'user' | 'assistant';
  content: string;
}

export interface ThreadAttachment {
  name: string;
  size?: number;
}

export interface ThreadDetailData extends ThreadSummary {
  contactFullName: string;
  module: string;
  messages: ChatMsg[];
  attachments: ThreadAttachment[];
}

const mocks = mockThreads as ThreadSummary[];

function toDetail(t: ThreadSummary): ThreadDetailData {
  return {
    ...t,
    contactFullName: 'Ana Torres',
    module: 'pagos',
    messages: [
      { key: `${t.id}-m1`, role: 'user', content: t.snippet },
      {
        key: `${t.id}-m2`,
        role: 'assistant',
        content:
          'Hola Ana, recibimos la propuesta de TechCorp (módulo pagos). La revisamos y te confirmamos el siguiente paso.',
      },
    ],
    attachments: [{ name: 'req_inicial.pdf', size: 48210 }],
  };
}

export async function getThreads(): Promise<ThreadSummary[]> {
  try {
    const res = await api.get('/threads');
    const data = res.data;
    const list = Array.isArray(data) ? data : data?.threads ?? data?.items;
    if (Array.isArray(list) && list.length > 0) return list as ThreadSummary[];
    return mocks;
  } catch {
    return mocks;
  }
}

export async function getThread(id: string): Promise<ThreadDetailData | null> {
  try {
    const res = await api.get(`/threads/${id}`);
    const data = res.data?.thread ?? res.data;
    if (data && data.id) {
      const base: ThreadSummary = {
        id: String(data.id),
        subject: String(data.subject ?? ''),
        from: String(data.from ?? ''),
        company: String(data.company ?? 'TechCorp'),
        contact: String(data.contact ?? 'Ana'),
        snippet: String(data.snippet ?? data.body ?? ''),
        date: String(data.date ?? ''),
        status: String(data.status ?? 'open'),
      };
      return toDetail(base);
    }
  } catch {
    // fallback a mock
  }
  const found = mocks.find((t) => t.id === id);
  return found ? toDetail(found) : null;
}
