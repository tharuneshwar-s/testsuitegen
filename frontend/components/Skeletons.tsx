export function SkeletonPipelineStatus() {
  return (
    <div className="mb-6 animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-stone-200 rounded-md"></div>
          <div>
            <div className="h-5 w-32 bg-stone-200 rounded mb-2"></div>
            <div className="h-3 w-24 bg-stone-100 rounded"></div>
          </div>
        </div>
        <div className="w-48">
          <div className="h-2 bg-stone-200 rounded-full mb-1"></div>
          <div className="h-3 w-12 bg-stone-100 rounded ml-auto"></div>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-stone-300 p-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-start gap-4 mb-3 last:mb-0">
            <div className="w-8 h-8 bg-stone-200 rounded-full shrink-0"></div>
            <div className="flex-1">
              <div className="h-4 w-40 bg-stone-200 rounded mb-2"></div>
              <div className="h-3 w-56 bg-stone-100 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonResults() {
  return (
    <div className="space-y-5 animate-pulse">
      {/* LLM Stats Skeleton */}
      <div className="bg-emerald-50 rounded-lg p-5 border border-emerald-200">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-4 h-4 bg-emerald-200 rounded"></div>
          <div className="h-4 w-32 bg-emerald-200 rounded"></div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i}>
              <div className="h-3 w-20 bg-emerald-100 rounded mb-2"></div>
              <div className="h-6 w-12 bg-emerald-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>

      {/* Operations Skeleton */}
      <div>
        <div className="h-4 w-40 bg-stone-200 rounded mb-3"></div>
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-white rounded-lg p-4 border border-stone-300"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  <div className="h-5 w-12 bg-sky-100 rounded"></div>
                  <div className="h-4 w-48 bg-stone-200 rounded"></div>
                </div>
                <div className="h-4 w-16 bg-stone-100 rounded"></div>
              </div>
              <div className="h-3 w-full bg-stone-100 rounded mb-2"></div>
              <div className="h-3 w-3/4 bg-stone-100 rounded"></div>
            </div>
          ))}
        </div>
      </div>

      {/* Test Cases Skeleton */}
      <div>
        <div className="h-4 w-36 bg-stone-200 rounded mb-3"></div>
        <div className="space-y-2">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="bg-white rounded-lg p-3 border border-stone-300"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 bg-emerald-100 rounded"></div>
                  <div className="h-4 w-64 bg-stone-200 rounded"></div>
                </div>
                <div className="h-6 w-16 bg-stone-100 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function SkeletonArtifacts() {
  return (
    <div className="animate-pulse">
      <div className="border-b border-stone-300 mb-4">
        <div className="flex gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-9 w-32 bg-stone-200 rounded-t"></div>
          ))}
        </div>
      </div>
      <div className="space-y-2">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
          <div
            key={i}
            className="h-4 bg-stone-100 rounded"
            style={{ width: `${Math.random() * 30 + 70}%` }}
          ></div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonEndpoints() {
  return (
    <div className="bg-white rounded-lg border border-stone-300 p-4 animate-pulse">
      <div className="h-5 w-40 bg-stone-200 rounded mb-4"></div>
      <div className="space-y-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-center gap-2">
            <div className="h-5 w-14 bg-sky-100 rounded"></div>
            <div className="h-4 flex-1 bg-stone-100 rounded"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonIntents() {
  return (
    <div className="space-y-2 animate-pulse">
      {[1, 2, 3, 4, 5].map((i) => (
        <div
          key={i}
          className="flex items-center gap-3 p-3 bg-white rounded-lg border border-stone-300"
        >
          <div className="w-4 h-4 bg-stone-200 rounded"></div>
          <div className="flex-1">
            <div className="h-4 w-40 bg-stone-200 rounded mb-1"></div>
            <div className="h-3 w-56 bg-stone-100 rounded"></div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-white rounded-lg border border-stone-300 p-4 animate-pulse">
      <div className="h-5 w-32 bg-stone-200 rounded mb-3"></div>
      <div className="space-y-2">
        <div className="h-4 bg-stone-100 rounded w-full"></div>
        <div className="h-4 bg-stone-100 rounded w-5/6"></div>
        <div className="h-4 bg-stone-100 rounded w-4/6"></div>
      </div>
    </div>
  );
}
