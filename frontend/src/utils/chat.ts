import type { ParsedAiSection } from '../types';

const SECTION_PATTERNS: { key: ParsedAiSection['key']; title: string; regex: RegExp }[] = [
  { key: 'facts', title: 'Facts', regex: /^\s*(facts?)\s*[:-]?\s*$/i },
  {
    key: 'observations',
    title: 'Observations',
    regex: /^\s*(observations?)\s*[:-]?\s*$/i,
  },
  { key: 'risks', title: 'Risks', regex: /^\s*(risks?)\s*[:-]?\s*$/i },
  {
    key: 'recommendations',
    title: 'Recommendations',
    regex: /^\s*(recommendations?|actions?)\s*[:-]?\s*$/i,
  },
];

function matchHeader(line: string): { key: ParsedAiSection['key']; title: string } | null {
  const stripped = line.replace(/[*#>_`]/g, '').trim();
  for (const pattern of SECTION_PATTERNS) {
    if (pattern.regex.test(stripped)) {
      return { key: pattern.key, title: pattern.title };
    }
  }
  // Also match "Facts: some inline text" style headers.
  const inline = stripped.match(/^(facts?|observations?|risks?|recommendations?|actions?)\s*:\s*(.+)$/i);
  if (inline) {
    const found = SECTION_PATTERNS.find((p) => p.regex.test(`${inline[1]}:`));
    if (found) return { key: found.key, title: found.title };
  }
  return null;
}

function cleanLine(line: string): string {
  return line.replace(/^\s*[-*•]\s?/, '').trim();
}

/**
 * Parses an AI assistant response into FACTS / OBSERVATIONS / RISKS /
 * RECOMMENDATIONS sections. If no recognizable headers are present the whole
 * message is returned as a single "other" section so it always renders.
 */
export function parseAiSections(content: string): ParsedAiSection[] {
  const lines = content.split(/\r?\n/);
  const sections: ParsedAiSection[] = [];
  let current: ParsedAiSection | null = null;

  for (const rawLine of lines) {
    const header = matchHeader(rawLine);
    if (header) {
      current = { key: header.key, title: header.title, lines: [] };
      sections.push(current);
      // Capture inline text after "Header: text"
      const inline = rawLine.replace(/[*#>_`]/g, '').match(/:\s*(.+)$/);
      if (inline && inline[1].trim()) {
        current.lines.push(cleanLine(inline[1]));
      }
      continue;
    }
    const text = cleanLine(rawLine);
    if (!text) continue;
    if (!current) {
      current = { key: 'other', title: 'Response', lines: [] };
      sections.push(current);
    }
    current.lines.push(text);
  }

  const meaningful = sections.filter((s) => s.lines.length > 0);
  if (meaningful.length === 0) {
    return [{ key: 'other', title: 'Response', lines: [content.trim()] }];
  }
  return meaningful;
}

export const SECTION_STYLES: Record<
  ParsedAiSection['key'],
  { label: string; badge: string; border: string }
> = {
  facts: {
    label: 'Facts',
    badge: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300',
    border: 'border-blue-300 dark:border-blue-800',
  },
  observations: {
    label: 'Observations',
    badge: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300',
    border: 'border-indigo-300 dark:border-indigo-800',
  },
  risks: {
    label: 'Risks',
    badge: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300',
    border: 'border-red-300 dark:border-red-800',
  },
  recommendations: {
    label: 'Recommendations',
    badge: 'bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300',
    border: 'border-green-300 dark:border-green-800',
  },
  other: {
    label: 'Response',
    badge: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    border: 'border-gray-200 dark:border-gray-700',
  },
};
