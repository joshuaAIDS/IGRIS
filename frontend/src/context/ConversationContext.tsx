import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { SupportedLanguage } from '../config/languages';
import { DEFAULT_MODEL_ID } from '../config/models';
import { BackendConnectionManager } from '../services/connection/connectionManager';
import {
  BackendHealthStatus,
  ChatMessage,
  InferenceChunk,
  InferenceConfig,
  TokenizeResponse,
} from '../services/inference/types';
import { detectLanguage } from '../utils/languageDetector';

export interface ConversationSession {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  modelId: string;
  language: SupportedLanguage;
  messages: ChatMessage[];
}

export interface ConversationContextType {
  sessions: ConversationSession[];
  activeSessionId: string;
  activeSession: ConversationSession | undefined;
  messages: ChatMessage[];
  isGenerating: boolean;
  error: string | null;
  activeLanguage: SupportedLanguage;
  inferenceConfig: InferenceConfig;
  backendStatus: BackendHealthStatus;
  customEndpointUrl: string;

  createNewSession: (modelId?: string) => string;
  switchSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  clearCurrentSession: () => void;
  sendMessage: (promptText: string, overrideLanguage?: SupportedLanguage) => Promise<void>;
  regenerateLastResponse: () => Promise<void>;
  stopGeneration: () => void;
  setActiveLanguage: (lang: SupportedLanguage) => void;
  setInferenceConfig: React.Dispatch<React.SetStateAction<InferenceConfig>>;
  setCustomEndpointUrl: (url: string) => void;
  setBackendMode: (mode: 'demo' | 'http') => void;
  checkBackendHealth: () => Promise<BackendHealthStatus>;
  tokenizeText: (text: string) => Promise<TokenizeResponse>;
  fetchModels: () => Promise<any[]>;
  dismissError: () => void;
}

const STORAGE_KEY = 'igris_conversation_sessions_v1';

function formatTimestamp(): string {
  const d = new Date();
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function createInitialSession(modelId = DEFAULT_MODEL_ID): ConversationSession {
  const now = new Date().toISOString();
  return {
    id: `S-${Date.now().toString(36).toUpperCase()}`,
    title: 'New Conversation',
    createdAt: now,
    updatedAt: now,
    modelId,
    language: 'en',
    messages: [],
  };
}

const ConversationContext = createContext<ConversationContextType | null>(null);

export const ConversationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const connectionMgr = useMemo(() => BackendConnectionManager.getInstance(), []);

  const [sessions, setSessions] = useState<ConversationSession[]>(() => {
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
          const parsed = JSON.parse(saved);
          if (Array.isArray(parsed) && parsed.length > 0) return parsed;
        }
      } catch (err) {
        console.warn('Failed to load saved sessions:', err);
      }
    }
    return [createInitialSession()];
  });

  const [activeSessionId, setActiveSessionId] = useState<string>(() => sessions[0]?.id || 'S-1');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeLanguage, setActiveLanguage] = useState<SupportedLanguage>('en');
  const [backendStatus, setBackendStatus] = useState<BackendHealthStatus>(connectionMgr.getStatus());
  const [customEndpointUrl, setCustomEndpointUrlState] = useState<string>(connectionMgr.getEndpointUrl());

  const [inferenceConfig, setInferenceConfig] = useState<InferenceConfig>({
    temperature: 0.7,
    maxTokens: 1024,
    topP: 0.9,
    streaming: true,
    returnUsage: true,
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  // Sync sessions to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
      } catch (err) {
        console.warn('Failed to save sessions to localStorage:', err);
      }
    }
  }, [sessions]);

  // Subscribe to backend status
  useEffect(() => {
    const unsubscribe = connectionMgr.subscribe((status) => {
      setBackendStatus(status);
    });
    return unsubscribe;
  }, [connectionMgr]);

  const activeSession = useMemo(
    () => sessions.find((s) => s.id === activeSessionId) || sessions[0],
    [sessions, activeSessionId],
  );

  const messages = activeSession?.messages || [];

  const createNewSession = useCallback(
    (modelId = DEFAULT_MODEL_ID) => {
      if (isGenerating && abortControllerRef.current) {
        abortControllerRef.current.abort();
        setIsGenerating(false);
      }
      const newSession = createInitialSession(modelId);
      setSessions((prev) => [newSession, ...prev]);
      setActiveSessionId(newSession.id);
      setError(null);
      return newSession.id;
    },
    [isGenerating],
  );

  const switchSession = useCallback(
    (sessionId: string) => {
      if (isGenerating && abortControllerRef.current) {
        abortControllerRef.current.abort();
        setIsGenerating(false);
      }
      const exists = sessions.some((s) => s.id === sessionId);
      if (exists) {
        setActiveSessionId(sessionId);
        setError(null);
      }
    },
    [isGenerating, sessions],
  );

  const deleteSession = useCallback(
    (sessionId: string) => {
      setSessions((prev) => {
        const filtered = prev.filter((s) => s.id !== sessionId);
        if (filtered.length === 0) {
          const fresh = createInitialSession();
          setActiveSessionId(fresh.id);
          return [fresh];
        }
        if (activeSessionId === sessionId) {
          setActiveSessionId(filtered[0].id);
        }
        return filtered;
      });
    },
    [activeSessionId],
  );

  const clearCurrentSession = useCallback(() => {
    if (isGenerating && abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsGenerating(false);
    }
    setSessions((prev) =>
      prev.map((s) =>
        s.id === activeSessionId
          ? {
              ...s,
              messages: [],
              updatedAt: new Date().toISOString(),
              title: 'New Conversation',
            }
          : s,
      ),
    );
    setError(null);
  }, [activeSessionId, isGenerating]);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    connectionMgr.getActiveAdapter().abort();
    setIsGenerating(false);
  }, [connectionMgr]);

  const sendMessage = useCallback(
    async (promptText: string, overrideLanguage?: SupportedLanguage) => {
      const cleanPrompt = promptText.trim();
      if (!cleanPrompt || isGenerating) return;

      const detectedLang = overrideLanguage || detectLanguage(cleanPrompt);
      setActiveLanguage(detectedLang);
      setError(null);

      const userMessageId = `u-${Date.now()}`;
      const assistantMessageId = `a-${Date.now() + 1}`;
      const timestamp = formatTimestamp();

      const userMsg: ChatMessage = {
        id: userMessageId,
        role: 'user',
        content: cleanPrompt,
        timestamp,
        language: detectedLang,
      };

      const initialAssistantMsg: ChatMessage = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        modelId: activeSession?.modelId || DEFAULT_MODEL_ID,
        timestamp,
        language: detectedLang,
        isDemo: connectionMgr.getActiveAdapter().isDemo,
      };

      // Auto title from prompt if first message
      const isFirstMessage = messages.length === 0;
      const titleCandidate =
        cleanPrompt.slice(0, 36) + (cleanPrompt.length > 36 ? '…' : '');

      setSessions((prev) =>
        prev.map((s) => {
          if (s.id !== activeSessionId) return s;
          return {
            ...s,
            title: isFirstMessage ? titleCandidate : s.title,
            language: detectedLang,
            updatedAt: new Date().toISOString(),
            messages: [...s.messages, userMsg, initialAssistantMsg],
          };
        }),
      );

      setIsGenerating(true);
      abortControllerRef.current = new AbortController();

      const adapter = connectionMgr.getActiveAdapter();

      try {
        const response = await adapter.sendMessage(
          {
            prompt: cleanPrompt,
            history: messages,
            modelId: activeSession?.modelId || DEFAULT_MODEL_ID,
            config: inferenceConfig,
            endpointUrl: customEndpointUrl,
            language: detectedLang,
          },
          (chunk: InferenceChunk) => {
            // Streaming chunk callback
            setSessions((prev) =>
              prev.map((s) => {
                if (s.id !== activeSessionId) return s;
                return {
                  ...s,
                  messages: s.messages.map((m) => {
                    if (m.id !== assistantMessageId) return m;
                    return {
                      ...m,
                      content: m.content + chunk.deltaText,
                      isDemo: chunk.isDemo ?? m.isDemo,
                    };
                  }),
                };
              }),
            );
          },
          abortControllerRef.current.signal,
        );

        // Finalize response
        setSessions((prev) =>
          prev.map((s) => {
            if (s.id !== activeSessionId) return s;
            return {
              ...s,
              messages: s.messages.map((m) => {
                if (m.id !== assistantMessageId) return m;
                return {
                  ...m,
                  content: response.text,
                  usage: response.usage,
                  isDemo: response.isDemo,
                  modelId: response.modelId,
                };
              }),
            };
          }),
        );
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          // Handled abort cleanly
          return;
        }
        const errMsg = err instanceof Error ? err.message : String(err);
        setError(errMsg);

        setSessions((prev) =>
          prev.map((s) => {
            if (s.id !== activeSessionId) return s;
            return {
              ...s,
              messages: s.messages.map((m) => {
                if (m.id !== assistantMessageId) return m;
                return {
                  ...m,
                  content: m.content || `⚠️ Error: ${errMsg}`,
                  error: true,
                };
              }),
            };
          }),
        );
      } finally {
        setIsGenerating(false);
        abortControllerRef.current = null;
      }
    },
    [
      activeSession?.modelId,
      activeSessionId,
      connectionMgr,
      customEndpointUrl,
      inferenceConfig,
      isGenerating,
      messages,
    ],
  );

  const regenerateLastResponse = useCallback(async () => {
    if (isGenerating || messages.length === 0) return;

    // Find the last user message
    let lastUserPrompt = '';
    let lastUserLang: SupportedLanguage | undefined;
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        lastUserPrompt = messages[i].content;
        lastUserLang = messages[i].language;
        break;
      }
    }

    if (!lastUserPrompt) return;

    // Remove the trailing assistant message if present
    setSessions((prev) =>
      prev.map((s) => {
        if (s.id !== activeSessionId) return s;
        const lastMsg = s.messages[s.messages.length - 1];
        const newMessages =
          lastMsg && lastMsg.role === 'assistant'
            ? s.messages.slice(0, -1)
            : s.messages;
        return {
          ...s,
          messages: newMessages,
        };
      }),
    );

    // Re-send prompt
    await sendMessage(lastUserPrompt, lastUserLang);
  }, [activeSessionId, isGenerating, messages, sendMessage]);

  const setCustomEndpointUrl = useCallback(
    (url: string) => {
      setCustomEndpointUrlState(url);
      connectionMgr.setEndpointUrl(url);
    },
    [connectionMgr],
  );

  const setBackendMode = useCallback(
    (mode: 'demo' | 'http') => {
      connectionMgr.setMode(mode);
    },
    [connectionMgr],
  );

  const checkBackendHealth = useCallback(async () => {
    return connectionMgr.checkHealth();
  }, [connectionMgr]);

  const tokenizeText = useCallback(
    async (text: string) => {
      return connectionMgr.tokenize(text);
    },
    [connectionMgr],
  );

  const fetchModels = useCallback(async () => {
    return connectionMgr.listModels();
  }, [connectionMgr]);

  const dismissError = useCallback(() => {
    setError(null);
  }, []);

  return (
    <ConversationContext.Provider
      value={{
        sessions,
        activeSessionId,
        activeSession,
        messages,
        isGenerating,
        error,
        activeLanguage,
        inferenceConfig,
        backendStatus,
        customEndpointUrl,
        createNewSession,
        switchSession,
        deleteSession,
        clearCurrentSession,
        sendMessage,
        regenerateLastResponse,
        stopGeneration,
        setActiveLanguage,
        setInferenceConfig,
        setCustomEndpointUrl,
        setBackendMode,
        checkBackendHealth,
        tokenizeText,
        fetchModels,
        dismissError,
      }}
    >
      {children}
    </ConversationContext.Provider>
  );
};

export function useConversation(): ConversationContextType {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error('useConversation must be used within a ConversationProvider');
  }
  return context;
}
