# IGRIS Chat & Model Interaction Interface

## 1. Overview

The official frontend foundation for **IGRIS (இக்ரிஸ்)** integrates the **Liquid Glass SLM Studio** interface, providing a high-fidelity visual workspace tailored for voice-first trilingual small language model interaction.

The interface preserves the original iOS-inspired Liquid Glass optical system, real-time procedural Three.js deep-space background, SVG chromatic displacement refraction filters, and responsive multi-device layouts.

---

## 2. Core Visual & Design Preservation

1. **iOS-Inspired Liquid Glass Material System**:
   - Layered frosted glass panels (`.frosted-glass`, `.frosted-glass-bright`, `.frosted-well`).
   - Specular inner lighting, 1px luminous borders, and backdrop-blur filtering.
   - Real-time cursor proximity refraction (`useLiquidGlassProximity`) dynamically shifting surface frost density as the pointer moves across components.
2. **Deep-Space Animated Background**:
   - Three.js WebGL canvas rendering starfields, cosmic nebula clouds, and smooth mouse parallax.
   - Preserves zero-distraction dark mode aesthetic (`#02030a`).
3. **SVG Chromatic Displacement Refraction Filter**:
   - Injected `<LiquidGlassFilter>` with configurable standard deviation blur for organic edge refraction.
4. **Responsive Layouts**:
   - Desktop: Persistent floating glass sidebar and multi-column workspace grid.
   - Mobile: Slide-over navigation drawer, responsive chat cards, and touch-optimized controls.

---

## 3. Chat Interface Capabilities

| Feature | Implementation Details |
| :--- | :--- |
| **New Conversation** | Instantly resets active prompt stream, creates a fresh session ID (`S-XXXX`), and preserves previous conversation in history. |
| **Conversation History** | Slide-out history drawer (`ConversationListDrawer`) persisting multi-session chat records in `localStorage`. Users can switch, preview, or delete past sessions. |
| **Trilingual Input** | Full native support for **Tamil Unicode (தமிழ்)**, **English**, and **Tanglish (Romanized Tamil)**. Includes a trilingual mode selector and heuristic script detector. |
| **Assistant Responses** | Structured frosted-well message bubbles featuring model branding, timestamp, formatted text, and Candidate A token usage metadata. |
| **Message Timestamps** | Formatted local time attached to every user and assistant message turn. |
| **Copy Response** | One-click copy button on every assistant bubble with animated visual confirmation (`Copied!`). |
| **Regenerate Response** | Button on the latest assistant response allowing immediate re-generation using the last user prompt. |
| **Stop Generation** | Dynamic action button that morphs into a pulsing stop icon during generation, immediately signaling `AbortController` cancellation. |
| **Clear Conversation** | Dedicated button to clear message history within the active conversation without deleting the session container. |
| **Streaming Responses** | True progressive token streaming with character/word pacing and animated typing cursor. |
| **Loading & Error States** | Pulsing status indicator during first-token latency; styled error banners with retry and dismiss options on runtime failure. |
| **Auto-Scroll** | Intelligent scrolling that tracks new message tokens automatically, but gracefully disengages if the user scrolls up to review prior messages. |
| **Markdown & Code Blocks** | Native Markdown renderer (`MarkdownRenderer`) supporting headings, bullet/numbered lists, bold, italics, blockquotes, inline code, and syntax-highlighted code blocks with individual copy buttons. |

---

## 4. Component Structure

```text
frontend/src/
├── components/
│   ├── background/
│   │   └── DeepSpaceBackground.tsx      # Three.js cosmic environment
│   ├── glass/                           # Liquid glass design system primitives
│   │   ├── GlassButton.tsx
│   │   ├── GlassCard.tsx
│   │   ├── GlassDropdown.tsx
│   │   ├── GlassIconButton.tsx
│   │   ├── GlassInputField.tsx
│   │   ├── GlassNavigationBar.tsx
│   │   ├── GlassNavigationItem.tsx
│   │   ├── GlassSlider.tsx
│   │   ├── GlassSwitch.tsx
│   │   └── LiquidGlassFilter.tsx
│   ├── chat/                            # Dedicated chat interface modules
│   │   ├── BackendStatusBadge.tsx       # Live connection indicator
│   │   ├── ChatComposer.tsx             # Trilingual input & stop/send button
│   │   ├── ChatMessageItem.tsx          # Message bubble & action toolbar
│   │   ├── ConversationListDrawer.tsx   # Multi-session history drawer
│   │   └── MarkdownRenderer.tsx         # Markdown & code block parser
│   └── studio/                          # High-level workspace cards and views
│       ├── CommandPaletteModal.tsx      # Cmd+K quick command modal
│       ├── InferenceControlsCard.tsx    # Temperature, Top-P, Max tokens
│       ├── MetricsStrip.tsx             # Real session token & latency telemetry
│       ├── ModelSelectionCard.tsx       # IGRIS model checkpoint selector
│       ├── PlaygroundPanel.tsx          # Core interactive playground
│       ├── RecentActivityCard.tsx       # Activity stream
│       ├── RuntimeMonitorCard.tsx       # GPU & VRAM hardware monitor
│       ├── Sidebar.tsx                  # Workspace navigation sidebar
│       ├── ThroughputChartCard.tsx      # Token throughput chart
│       └── WorkspaceViews.tsx           # Multi-tab workspace views
```
