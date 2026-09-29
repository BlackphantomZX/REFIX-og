import { useMemo } from "react";
import { SearchIcon, CheckIcon } from "./Icons";

export default function DeviceStep({ devices, brands, search, setSearch, brandFilter, setBrandFilter, selectedDeviceId, onSelectDevice }) {
  const matches = useMemo(() => {
    const q = search.trim().toLowerCase();
    return devices.filter((d) => {
      if (brandFilter && d.brand !== brandFilter) return false;
      if (!q) return true;
      return d.model.toLowerCase().includes(q) || d.brand.toLowerCase().includes(q);
    });
  }, [devices, search, brandFilter]);

  return (
    <main className="step-main">
      <p className="step-eyebrow">Find out how much your phone repair might cost</p>
      <h1 className="step-title">What device do you have?</h1>
      <p className="step-sub">
        Search your model, or filter by brand below. No account or personal details needed.
      </p>

      <div className="search-wrap">
        <SearchIcon />
        <input
          type="text"
          placeholder="Search your phone model, e.g. iPhone 13"
          value={search}
          autoComplete="off"
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="brand-chip-row">
        <button className={`chip ${!brandFilter ? "active" : ""}`} onClick={() => setBrandFilter("")}>
          All brands
        </button>
        {brands.map((b) => (
          <button key={b} className={`chip ${brandFilter === b ? "active" : ""}`} onClick={() => setBrandFilter(b)}>
            {b}
          </button>
        ))}
      </div>

      <div>
        {matches.length ? (
          matches.map((d) => (
            <button
              key={d.id}
              className={`row-btn ${selectedDeviceId === d.id ? "selected" : ""}`}
              onClick={() => onSelectDevice(d)}
            >
              <span className="row-main">
                <span className="row-title">{d.model}</span>
                <span className="row-meta">{d.brand}</span>
              </span>
              <span className="row-check">
                <CheckIcon />
              </span>
            </button>
          ))
        ) : (
          <div className="empty-note">
            We don't have pricing information for that search yet. Try a different model or brand.
          </div>
        )}
      </div>
    </main>
  );
}
