import hljs from "highlight.js/lib/core";
import bash from "highlight.js/lib/languages/bash";
import css from "highlight.js/lib/languages/css";
import go from "highlight.js/lib/languages/go";
import java from "highlight.js/lib/languages/java";
import javascript from "highlight.js/lib/languages/javascript";
import json from "highlight.js/lib/languages/json";
import markdown from "highlight.js/lib/languages/markdown";
import python from "highlight.js/lib/languages/python";
import rust from "highlight.js/lib/languages/rust";
import sql from "highlight.js/lib/languages/sql";
import typescript from "highlight.js/lib/languages/typescript";
import xml from "highlight.js/lib/languages/xml";
import yaml from "highlight.js/lib/languages/yaml";

const LANGUAGES: Record<string, Parameters<typeof hljs.registerLanguage>[1]> = {
  javascript,
  js: javascript,
  typescript,
  ts: typescript,
  tsx: typescript,
  jsx: javascript,
  python,
  py: python,
  bash,
  sh: bash,
  shell: bash,
  json,
  sql,
  css,
  html: xml,
  xml,
  yaml,
  yml: yaml,
  rust,
  rs: rust,
  go,
  java,
  markdown,
  md: markdown,
};

for (const [name, lang] of Object.entries(LANGUAGES)) {
  if (!hljs.getLanguage(name)) {
    hljs.registerLanguage(name, lang);
  }
}

/** Highlight source code with highlight.js. */
export function highlightCode(code: string, language?: string): string {
  const trimmed = code.replace(/\n$/, "");

  if (language && hljs.getLanguage(language)) {
    try {
      return hljs.highlight(trimmed, { language }).value;
    } catch {
      // fall through
    }
  }

  try {
    return hljs.highlightAuto(trimmed).value;
  } catch {
    return trimmed
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
}

export { hljs };
