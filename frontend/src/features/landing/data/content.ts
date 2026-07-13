/** Landing page content and navigation anchors. */

export const LANDING_TAGLINE = "The AI that tells you the truth.";

export const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "How it works", href: "#how-it-works" },
  { label: "Compare", href: "#compare" },
  { label: "FAQ", href: "#faq" },
] as const;

export const HERO = {
  headline: "The AI that tells you the truth.",
  subheadline:
    "Reasoning Engine challenges flawed assumptions, surfaces evidence gaps, and refuses to flatter you into bad decisions.",
  primaryCta: "Start reasoning",
  secondaryCta: "See how it works",
} as const;

export const FEATURES = [
  {
    title: "Anti-sycophancy by design",
    description:
      "Built to disagree when your reasoning is weak — not to validate every opinion for the sake of rapport.",
    icon: "shield" as const,
  },
  {
    title: "Multi-stage reasoning",
    description:
      "Every response passes through classification, claim extraction, fallacy detection, and confidence scoring.",
    icon: "layers" as const,
  },
  {
    title: "Debate-grade analysis",
    description:
      "Support, opposition, fact-checking, and judge agents stress-test conclusions before you act on them.",
    icon: "scale" as const,
  },
  {
    title: "Calibrated confidence",
    description:
      "See exactly how certain the model is — and why — instead of getting false precision.",
    icon: "gauge" as const,
  },
  {
    title: "Memory with integrity",
    description:
      "Long-term context that detects contradictions and asks clarifying questions instead of silently overwriting facts.",
    icon: "brain" as const,
  },
  {
    title: "Open & auditable",
    description:
      "Self-hosted models, structured reasoning traces, and evaluation benchmarks you can actually run.",
    icon: "code" as const,
  },
] as const;

export const STEPS = [
  {
    step: "01",
    title: "Ask anything",
    description: "Pose a question, share a plan, or challenge an idea you are unsure about.",
  },
  {
    step: "02",
    title: "Reasoning pipeline runs",
    description:
      "Claims, assumptions, and fallacies are extracted before a response is generated.",
  },
  {
    step: "03",
    title: "Get an honest answer",
    description:
      "Receive a direct response with confidence scores, evidence gaps, and reasoning you can inspect.",
  },
] as const;

export const COMPARISON = {
  traditional: [
    "Agrees to keep you engaged",
    "Invents facts when uncertain",
    "Hides reasoning behind fluent prose",
    "Optimizes for satisfaction, not accuracy",
    "Rarely challenges your assumptions",
  ],
  reasoningEngine: [
    "Challenges weak logic respectfully",
    "Flags unknowns instead of guessing",
    "Shows structured reasoning traces",
    "Optimizes for truth and calibration",
    "Surfaces contradictions in your thinking",
  ],
} as const;

export const FAQ_ITEMS = [
  {
    question: "How is this different from ChatGPT or Claude?",
    answer:
      "Traditional assistants are tuned for helpfulness and engagement, which often means agreement. Reasoning Engine is tuned for critical thinking — it runs a multi-stage analysis pipeline and is explicitly prompted not to flatter you when the evidence does not support your position.",
  },
  {
    question: "Will it always disagree with me?",
    answer:
      "No. When you are right and the evidence supports your view, it agrees. The difference is that agreement is earned through reasoning, not assumed by default.",
  },
  {
    question: "Can I self-host the models?",
    answer:
      "Yes. The backend supports vLLM and Hugging Face Transformers, so you can run Qwen, Llama, or other open-weight models on your own infrastructure.",
  },
  {
    question: "What is reasoning mode vs chat mode?",
    answer:
      "Chat mode streams direct responses with the anti-sycophancy persona. Reasoning mode runs the full pipeline — classification, claims, fallacies, confidence scoring — and shows you the trace.",
  },
  {
    question: "Is my conversation data stored?",
    answer:
      "Conversations are stored locally in your browser by default. Backend persistence is available when connected to PostgreSQL for memory and contradiction detection features.",
  },
] as const;

export const CTA = {
  headline: "Ready for honest answers?",
  subheadline: "Stop getting validated. Start getting reasoned with.",
  button: "Open Reasoning Engine",
} as const;

export const FOOTER = {
  tagline: "Built for people who prefer truth over comfort.",
  links: [
    { label: "Documentation", href: "https://github.com" },
    { label: "API", href: "/api/docs" },
    { label: "GitHub", href: "https://github.com" },
  ],
} as const;
