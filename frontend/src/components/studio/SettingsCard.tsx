import React, { useState } from 'react';
import {
  Check,
  Globe,
  Palette,
  RefreshCw,
  Server,
  Sliders,
  Trash2,
} from 'lucide-react';
import { SupportedLanguage, SUPPORTED_LANGUAGES } from '../../config/languages';
import { useConversation } from '../../context/ConversationContext';
import { GlassButton } from '../glass/GlassButton';
import { GlassCard } from '../glass/GlassCard';
import { GlassInputField } from '../glass/GlassInputField';
import { GlassSlider } from '../glass/GlassSlider';
import { GlassSwitch } from '../glass/GlassSwitch';

interface SettingsCardProps {
  customEndpointUrl: string;
  backendMode: 'demo' | 'http';
  backendConnected: boolean;
  glassFrost: number;
  glassBlur: number;
  onUpdateEndpointUrl: (url: string) => void;
  onUpdateBackendMode: (mode: 'demo' | 'http') => void;
  onTestBackendConnection: () => Promise<void>;
  onUpdateGlassSettings: (frost: number, blur: number) => void;
}

export function SettingsCard({
  customEndpointUrl,
  backendMode,
  backendConnected,
  glassFrost,
  glassBlur,
  onUpdateEndpointUrl,
  onUpdateBackendMode,
  onTestBackendConnection,
  onUpdateGlassSettings,
}: SettingsCardProps) {
  const {
    activeLanguage,
    setActiveLanguage,
    inferenceConfig,
    setInferenceConfig,
    clearCurrentSession,
    sessions,
  } = useConversation();

  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);
  const [autoDetectLanguage, setAutoDetectLanguage] = useState(true);
  const [clearedNotice, setClearedNotice] = useState(false);

  const handleTest = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      await onTestBackendConnection();
      setTestResult('Connection healthy · Candidate A verified');
    } catch (err) {
      setTestResult(`Connection failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsTesting(false);
    }
  };

  const handleClearHistory = () => {
    clearCurrentSession();
    setClearedNotice(true);
    setTimeout(() => setClearedNotice(false), 2400);
  };

  const handleResetDefaults = () => {
    onUpdateGlassSettings(0.1, 26);
    setInferenceConfig({
      temperature: 0.7,
      maxTokens: 1024,
      topP: 0.9,
      streaming: true,
      returnUsage: true,
    });
    setActiveLanguage('en');
    onUpdateBackendMode('http');
    onUpdateEndpointUrl('http://127.0.0.1:8000/v1/chat/completions');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* 1. Theme & Optics */}
      <GlassCard rounded="2xl" className="p-5 space-y-4">
        <div className="flex items-center gap-2 pb-2 border-b border-white/10">
          <Palette size={16} className="text-[#82ecff]" />
          <div>
            <h2 className="text-sm font-bold text-white m-0">Theme & Optical Calibration</h2>
            <p className="text-xs text-white/70 m-0">
              Calibrate frosted glass refractive density and backdrop blur over the deep space environment.
            </p>
          </div>
        </div>

        <GlassSlider
          id="surface-frost-slider"
          label="Surface Frost Density"
          value={glassFrost}
          displayValue={`${Math.round(glassFrost * 100)}%`}
          min={0.06}
          max={0.28}
          step={0.02}
          onChange={(val) => onUpdateGlassSettings(val, glassBlur)}
        />

        <GlassSlider
          id="backdrop-blur-slider"
          label="Backdrop Blur Radius"
          value={glassBlur}
          displayValue={`${glassBlur} px`}
          min={16}
          max={38}
          step={2}
          onChange={(val) => onUpdateGlassSettings(glassFrost, val)}
        />

        <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-xs text-white/60">
          Proximity refraction dynamically responds to mouse cursor position across all cards.
        </div>
      </GlassCard>

      {/* 2. Trilingual Language Preferences */}
      <GlassCard rounded="2xl" className="p-5 space-y-4">
        <div className="flex items-center gap-2 pb-2 border-b border-white/10">
          <Globe size={16} className="text-[#72eab8]" />
          <div>
            <h2 className="text-sm font-bold text-white m-0">Language Preferences</h2>
            <p className="text-xs text-white/70 m-0">
              Configure default language and trilingual boundaries for IGRIS.
            </p>
          </div>
        </div>

        <div className="space-y-1.5">
          <label htmlFor="settings-language-select" className="block text-xs font-medium text-white/80">
            Default Trilingual Mode
          </label>
          <div className="relative">
            <select
              id="settings-language-select"
              value={activeLanguage}
              onChange={(e) => setActiveLanguage(e.target.value as SupportedLanguage)}
              className="w-full px-3 py-2.5 rounded-xl bg-black/40 border border-white/20 text-white text-xs font-medium focus:outline-none focus:border-[#82ecff]"
            >
              {SUPPORTED_LANGUAGES.map((lang) => (
                <option key={lang.id} value={lang.id} className="bg-[#0b1022] text-white">
                  {lang.badge} — {lang.nativeName} ({lang.name})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/10">
          <div>
            <div className="text-xs font-medium text-white">Auto-Detect Prompt Script</div>
            <div className="text-[11px] text-white/60">Detects Tamil Unicode vs Romanized Tanglish vs English</div>
          </div>
          <GlassSwitch
            id="auto-detect-lang-switch"
            checked={autoDetectLanguage}
            onChange={(checked) => setAutoDetectLanguage(checked)}
          />
        </div>

        <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/20 text-xs text-cyan-200/90 leading-relaxed">
          <strong>Strict Linguistic Boundary:</strong> IGRIS is strictly optimized for Tamil, English, and Tanglish.
          Other languages (French, Spanish, Hindi, etc.) are excluded by architectural specification.
        </div>
      </GlassCard>

      {/* 3. Generation Controls */}
      <GlassCard rounded="2xl" className="p-5 space-y-4">
        <div className="flex items-center gap-2 pb-2 border-b border-white/10">
          <Sliders size={16} className="text-[#f5c879]" />
          <div>
            <h2 className="text-sm font-bold text-white m-0">Generation Controls</h2>
            <p className="text-xs text-white/70 m-0">
              Adjust sampling temperature, nucleus probability, and output limits.
            </p>
          </div>
        </div>

        <GlassSlider
          id="settings-temp-slider"
          label="Sampling Temperature"
          value={inferenceConfig.temperature}
          displayValue={inferenceConfig.temperature.toFixed(2)}
          min={0.0}
          max={1.5}
          step={0.05}
          onChange={(val) => setInferenceConfig((c) => ({ ...c, temperature: val }))}
        />

        <GlassSlider
          id="settings-topp-slider"
          label="Top-P (Nucleus Sampling)"
          value={inferenceConfig.topP}
          displayValue={inferenceConfig.topP.toFixed(2)}
          min={0.1}
          max={1.0}
          step={0.05}
          onChange={(val) => setInferenceConfig((c) => ({ ...c, topP: val }))}
        />

        <GlassSlider
          id="settings-maxtok-slider"
          label="Maximum Output Tokens"
          value={inferenceConfig.maxTokens}
          displayValue={`${inferenceConfig.maxTokens} tok`}
          min={64}
          max={2048}
          step={64}
          onChange={(val) => setInferenceConfig((c) => ({ ...c, maxTokens: val }))}
        />

        <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/10">
          <div>
            <div className="text-xs font-medium text-white">Server-Sent Events (SSE) Streaming</div>
            <div className="text-[11px] text-white/60">Stream tokens progressively as they are generated</div>
          </div>
          <GlassSwitch
            id="settings-streaming-switch"
            checked={inferenceConfig.streaming}
            onChange={(checked) => setInferenceConfig((c) => ({ ...c, streaming: checked }))}
          />
        </div>
      </GlassCard>

      {/* 4. Backend Connection & Reset */}
      <GlassCard rounded="2xl" className="p-5 space-y-4">
        <div className="flex items-center gap-2 pb-2 border-b border-white/10">
          <Server size={16} className="text-[#a9f1ff]" />
          <div>
            <h2 className="text-sm font-bold text-white m-0">Inference Gateway & Session State</h2>
            <p className="text-xs text-white/70 m-0">
              Configure communication with the local IGRIS inference runtime daemon.
            </p>
          </div>
        </div>

        {/* Backend Mode Toggle */}
        <div className="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-white/80 font-medium">Inference Execution Mode</span>
            <span
              className={`font-mono-tabular text-[10px] font-bold ${
                backendMode === 'http' ? 'text-[#72eab8]' : 'text-[#f5c879]'
              }`}
            >
              {backendMode === 'http' ? 'LIVE RUNTIME DAEMON' : 'DEMO SIMULATION'}
            </span>
          </div>
          <div className="flex gap-2 pt-1">
            <GlassButton
              size="sm"
              variant={backendMode === 'demo' ? 'primary' : 'glass'}
              className="flex-1 justify-center"
              onClick={() => onUpdateBackendMode('demo')}
            >
              Demo Simulation
            </GlassButton>
            <GlassButton
              size="sm"
              variant={backendMode === 'http' ? 'primary' : 'glass'}
              className="flex-1 justify-center"
              onClick={() => onUpdateBackendMode('http')}
            >
              Local HTTP Runtime
            </GlassButton>
          </div>
        </div>

        <div className="space-y-1.5">
          <label htmlFor="settings-endpoint-input" className="block text-xs font-medium text-white/80">
            Inference Runtime Endpoint URL
          </label>
          <GlassInputField
            id="settings-endpoint-input"
            value={customEndpointUrl}
            onChange={(e) => onUpdateEndpointUrl(e.target.value)}
            placeholder="http://127.0.0.1:8000/v1/chat/completions"
          />
        </div>

        <div className="flex items-center justify-between gap-2 pt-1">
          <GlassButton
            size="sm"
            variant="glass"
            onClick={handleTest}
            disabled={isTesting}
          >
            <RefreshCw size={13} className={isTesting ? 'animate-spin' : ''} />
            <span>{isTesting ? 'Testing...' : 'Test Connection'}</span>
          </GlassButton>

          {testResult && (
            <span className="font-mono-tabular text-[10px] text-[#a9f1ff] truncate max-w-[240px]">
              {testResult}
            </span>
          )}
        </div>

        <div className="pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-2">
          <button
            type="button"
            onClick={handleClearHistory}
            className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 font-mono-tabular cursor-pointer transition-colors"
          >
            <Trash2 size={13} />
            <span>Clear History ({sessions.length} sessions)</span>
          </button>
          {clearedNotice && (
            <span className="text-[10px] text-[#72eab8] font-mono-tabular">History cleared</span>
          )}

          <button
            type="button"
            onClick={handleResetDefaults}
            className="text-xs text-white/50 hover:text-white font-mono-tabular cursor-pointer transition-colors"
          >
            Reset Defaults
          </button>
        </div>
      </GlassCard>
    </div>
  );
}