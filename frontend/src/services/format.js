// Presentation-only helpers. All pricing/estimation logic lives in the
// backend (backend/services/estimator.py) -- nothing here should compute a
// price, only format numbers the API already returned.

export function fmtINR(amount) {
  if (amount === null || amount === undefined) return "\u2014";
  return "\u20B9" + Math.round(amount).toLocaleString("en-IN");
}

export function cap(str) {
  if (!str) return "";
  return str.charAt(0).toUpperCase() + str.slice(1);
}
