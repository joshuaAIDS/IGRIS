import { Activity, AlertTriangle, CheckCircle, Radio } from 'lucide-react';
import { BackendHealthStatus } from '../../services/inference/types';

interface BackendStatusBadgeProps {
  status: BackendHealthStatus;
  isGenerating?: boolean;
  onClickSettings?: () => void;
}

export function BackendStatusBadge({
  status,
  isGenerating = false,
  onClickSettings,
}: BackendStatusBadgeProps) {
  // 1. Generation Active State
  if (isGenerating) {
    return (
      <div
        onClick={onClickSettings}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#5fc5ff]/20 border border-[#5fc5ff]/45 text-[#5fc5ff] font-mono-tabular text-[10px] cursor-pointer hover:bg-[#5fc5ff]/30 transition-all shadow-[0_0_12px_rgba(95,197,255,0.25)] animate-pulse"
        title="IGRIS is actively generating tokens..."
      >
        <span className="w-1.5 h-1.5 rounded-full bg-[#5fc5ff] animate-ping" />
        <Activity size={11} className="animate-spin text-[#5fc5ff]" />
        <span>MODEL GENERATING</span>
      </div>
    );
  }

  // 2. Demo Simulation State
  if (status.isDemo) {
    return (
      <div
        onClick={onClickSettings}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#f5c879]/15 border border-[#f5c879]/35 text-[#f5c879] font-mono-tabular text-[10px] cursor-pointer hover:bg-[#f5c879]/25 transition-all"
        title="IGRIS Demo Simulation Mode. Click to configure live runtime in Settings."
      >
        <Radio size={11} className="text-[#f5c879]" />
        <span>DEMO MODE</span>
      </div>
    );
  }

  // 3. Connected State (Either MODEL LOADED or MODEL NOT TRAINED)
  if (status.isConnected) {
    if (status.modelState === 'MODEL LOADED' || status.isTrained) {
      return (
        <div
          onClick={onClickSettings}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#72eab8]/15 border border-[#72eab8]/35 text-[#72eab8] font-mono-tabular text-[10px] cursor-pointer hover:bg-[#72eab8]/25 transition-all shadow-[0_0_10px_rgba(114,234,184,0.15)]"
          title={`Connected to ${status.endpoint} (${status.latencyMs ?? 0}ms). Model weights loaded.`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[#72eab8]" />
          <CheckCircle size={11} />
          <span>MODEL LOADED</span>
          {status.latencyMs !== undefined && <span>({status.latencyMs}ms)</span>}
        </div>
      );
    }

    // Connected to runtime daemon, but no checkpoint weights loaded yet
    return (
      <div
        onClick={onClickSettings}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#ffb86c]/20 border border-[#ffb86c]/45 text-[#ffb86c] font-mono-tabular text-[10px] cursor-pointer hover:bg-[#ffb86c]/30 transition-all shadow-[0_0_10px_rgba(255,184,108,0.2)]"
        title="Connected to IGRIS local runtime daemon. Candidate A tokenizer & architecture verified, but weights are not trained yet."
      >
        <AlertTriangle size={11} className="text-[#ffb86c]" />
        <span>MODEL NOT TRAINED</span>
        {status.latencyMs !== undefined && <span>({status.latencyMs}ms)</span>}
      </div>
    );
  }

  // 4. Disconnected State
  return (
    <div
      onClick={onClickSettings}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#ff8ea8]/15 border border-[#ff8ea8]/35 text-[#ff8ea8] font-mono-tabular text-[10px] cursor-pointer hover:bg-[#ff8ea8]/25 transition-all"
      title={`Connection failed: ${status.error || 'Runtime offline'}. Click to configure in Settings.`}
    >
      <AlertTriangle size={11} />
      <span>BACKEND: DISCONNECTED</span>
    </div>
  );
}
