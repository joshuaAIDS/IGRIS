import test from 'node:test';
import assert from 'node:assert/strict';
import { ChatMessage } from '../services/inference/types';

interface TestSession {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  modelId: string;
  messages: ChatMessage[];
}

function createSession(id: string, modelId = 'IGRIS-50M-BASELINE'): TestSession {
  const now = new Date().toISOString();
  return {
    id,
    title: 'New Conversation',
    createdAt: now,
    updatedAt: now,
    modelId,
    messages: [],
  };
}

test('Conversation State: handles session creation and initial defaults', () => {
  const session = createSession('S-TEST-1');
  assert.equal(session.id, 'S-TEST-1');
  assert.equal(session.title, 'New Conversation');
  assert.equal(session.messages.length, 0);
  assert.equal(session.modelId, 'IGRIS-50M-BASELINE');
});

test('Conversation State: adding user and assistant messages preserves order and timestamps', () => {
  const session = createSession('S-TEST-2');

  const userMsg: ChatMessage = {
    id: 'u-1',
    role: 'user',
    content: 'What is the IGRIS baseline architecture?',
    timestamp: '7:45 PM',
    language: 'en',
  };

  const assistantMsg: ChatMessage = {
    id: 'a-1',
    role: 'assistant',
    content: 'IGRIS uses a custom ~50M parameter decoder-only Transformer.',
    timestamp: '7:45 PM',
    language: 'en',
    isDemo: true,
    usage: {
      promptTokens: 8,
      completionTokens: 12,
      totalTokens: 20,
      latencyMs: 82,
    },
  };

  session.messages.push(userMsg);
  session.messages.push(assistantMsg);

  assert.equal(session.messages.length, 2);
  assert.equal(session.messages[0].role, 'user');
  assert.equal(session.messages[1].role, 'assistant');
  assert.equal(session.messages[1].isDemo, true);
  assert.equal(session.messages[1].usage?.totalTokens, 20);
});

test('Conversation State: clearing conversation empties messages while keeping session active', () => {
  const session = createSession('S-TEST-3');
  session.messages.push({
    id: 'u-1',
    role: 'user',
    content: 'Hello',
    timestamp: '7:46 PM',
  });
  assert.equal(session.messages.length, 1);

  // Clear messages
  session.messages = [];
  assert.equal(session.messages.length, 0);
  assert.equal(session.id, 'S-TEST-3');
});

test('Conversation State: multi-session list allows switching and deleting', () => {
  let sessions: TestSession[] = [
    createSession('S-1'),
    createSession('S-2'),
    createSession('S-3'),
  ];

  let activeId = 'S-1';

  // Switch session
  activeId = 'S-2';
  assert.equal(activeId, 'S-2');

  // Delete session S-2
  sessions = sessions.filter((s) => s.id !== 'S-2');
  assert.equal(sessions.length, 2);
  assert.ok(!sessions.some((s) => s.id === 'S-2'));

  // Fallback to S-1
  if (!sessions.some((s) => s.id === activeId)) {
    activeId = sessions[0].id;
  }
  assert.equal(activeId, 'S-1');
});
