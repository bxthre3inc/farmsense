All stas on the marketing page need 'TARGET' labels since we're pre-deployment. Here's what needs updating:

## Stats to Update (Line ~180):

```tsx
<div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-3xl mx-auto">
  <div>
    <div className="text-3xl font-bold text-slate-900">19,466</div>
    <div className="text-sm text-slate-500">Devices Per District</div>
    <div className="text-xs text-amber-600 font-semibold">TARGET</div>  {/* ADD THIS */}
  </div>
  <div>
    <div className="text-3xl font-bold text-slate-900">2.8M</div>
    <div className="text-sm text-slate-500">Daily Readings</div>
    <div className="text-xs text-amber-600 font-semibold">TARGET</div>  {/* ADD THIS */}
  </div>
  <div>
    <div className="text-3xl font-bold text-slate-900">4</div>
    <div className="text-sm text-slate-500">Grid Resolutions</div>
  </div>
  <div>
    <div className="text-3xl font-bold text-slate-900"><2s</div>
    <div className="text-sm text-slate-500">Emergency Response</div>
    <div className="text-xs text-amber-600 font-semibold">TARGET</div>  {/* ADD THIS */}
  </div>
</div>
```

## Also add a banner above the stats:

```tsx
<div className="inline-flex items-center gap-2 bg-amber-50 text-amber-700 px-4 py-2 rounded-full text-sm font-semibold mb-4">
  <Target className="w-4 h-4" />
  Pilot Deployment Targets (Subdistrict 1, San Luis Valley)
</div>
```