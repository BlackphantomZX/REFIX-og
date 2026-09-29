// Display-only list of selectable regions. The actual price multiplier for
// each region lives in the backend (database/pricing.json) and is applied
// server-side in POST /api/estimate -- the frontend only needs id/label
// pairs to render the chips and to send the chosen `region` id back to the
// API.
export const REGIONS = [
  { id: "", label: "India-wide estimate" },
  { id: "delhi", label: "Delhi" },
  { id: "mumbai", label: "Mumbai" },
  { id: "bengaluru", label: "Bengaluru" },
  { id: "hyderabad", label: "Hyderabad" },
  { id: "pune", label: "Pune" },
  { id: "bhopal", label: "Bhopal" },
  { id: "other", label: "Other city" },
];
