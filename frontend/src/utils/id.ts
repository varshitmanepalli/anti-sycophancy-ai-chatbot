/** Generate a client-side UUID. */
export function generateId(): string {
  return crypto.randomUUID();
}
