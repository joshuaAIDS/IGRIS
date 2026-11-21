import { IInferenceAdapter } from '../inference/adapter.interface';
import { DemoSimulationAdapter } from '../inference/demoAdapter';
import { IgrisHttpBackendAdapter } from '../inference/httpAdapter';
import { BackendHealthStatus, TokenizeResponse } from '../inference/types';

export type BackendMode = 'demo' | 'http';

export class BackendConnectionManager {
  private static instance: BackendConnectionManager;

  private mode: BackendMode = 'demo';
  private endpointUrl: string = 'http://127.0.0.1:8000/v1/chat/completions';
  private demoAdapter: DemoSimulationAdapter;
  private httpAdapter: IgrisHttpBackendAdapter;
  private status: BackendHealthStatus;
  private listeners: Set<(status: BackendHealthStatus) => void> = new Set();

  private constructor() {
    this.demoAdapter = new DemoSimulationAdapter();
    this.httpAdapter = new IgrisHttpBackendAdapter();

    // Check localStorage for saved settings if in browser
    if (typeof window !== 'undefined') {
      const savedEndpoint = localStorage.getItem('igris_endpoint_url');
      if (savedEndpoint) {
        this.endpointUrl = savedEndpoint;
      }
      const savedMode = localStorage.getItem('igris_backend_mode') as BackendMode;
      if (savedMode === 'http' || savedMode === 'demo') {
        this.mode = savedMode;
      }
    }

    this.status = {
      isConnected: false,
      isDemo: this.mode === 'demo',
      endpoint: this.endpointUrl,
      statusText: this.mode === 'demo' ? 'DEMO MODE · LOCAL RUNTIME STANDBY' : 'DISCONNECTED · STANDBY',
    };
  }

  public static getInstance(): BackendConnectionManager {
    if (!BackendConnectionManager.instance) {
      BackendConnectionManager.instance = new BackendConnectionManager();
    }
    return BackendConnectionManager.instance;
  }

  public getActiveAdapter(): IInferenceAdapter {
    if (this.mode === 'http') {
      return this.httpAdapter;
    }
    return this.demoAdapter;
  }

  public getMode(): BackendMode {
    return this.mode;
  }

  public setMode(mode: BackendMode): void {
    this.mode = mode;
    if (typeof window !== 'undefined') {
      localStorage.setItem('igris_backend_mode', mode);
    }
    this.checkHealth();
  }

  public getEndpointUrl(): string {
    return this.endpointUrl;
  }

  public setEndpointUrl(url: string): void {
    this.endpointUrl = url;
    if (typeof window !== 'undefined') {
      localStorage.setItem('igris_endpoint_url', url);
    }
    this.checkHealth();
  }

  public getStatus(): BackendHealthStatus {
    return this.status;
  }

  public subscribe(listener: (status: BackendHealthStatus) => void): () => void {
    this.listeners.add(listener);
    listener(this.status);
    return () => {
      this.listeners.delete(listener);
    };
  }

  public async checkHealth(): Promise<BackendHealthStatus> {
    if (this.mode === 'demo') {
      const demoStatus = await this.demoAdapter.checkHealth();
      this.status = demoStatus;
      this.notifyListeners();
      return demoStatus;
    }

    const httpStatus = await this.httpAdapter.checkHealth(this.endpointUrl);
    this.status = httpStatus;
    this.notifyListeners();
    return httpStatus;
  }

  public async tokenize(text: string): Promise<TokenizeResponse> {
    return this.httpAdapter.tokenize(text, this.endpointUrl);
  }

  public async listModels(): Promise<any[]> {
    return this.httpAdapter.listModels(this.endpointUrl);
  }

  private notifyListeners(): void {
    for (const listener of this.listeners) {
      try {
        listener(this.status);
      } catch (err) {
        console.error('Error in backend connection listener:', err);
      }
    }
  }
}
