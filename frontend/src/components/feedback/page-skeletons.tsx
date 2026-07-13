import { ShimmerSkeleton, SkeletonAvatar, SkeletonText } from "./shimmer-skeleton";

/** Chat message area skeleton. */
export function ChatMessagesSkeleton() {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-8" aria-label="Loading chat">
      {[0, 1, 2].map((index) => (
        <div key={index} className="flex gap-3">
          <SkeletonAvatar className="h-8 w-8" />
          <div className="flex-1 space-y-2">
            <ShimmerSkeleton className="h-4 w-24" />
            <ShimmerSkeleton className={index === 1 ? "h-24 w-full" : index === 0 ? "h-16 w-full" : "h-12 w-3/4"} />
          </div>
        </div>
      ))}
    </div>
  );
}

/** Dashboard header + content skeleton. */
export function DashboardPageSkeleton() {
  return (
    <div className="flex h-dvh flex-col bg-background" aria-label="Loading dashboard">
      <div className="flex h-14 items-center justify-between border-b px-4">
        <ShimmerSkeleton className="h-5 w-32" />
        <div className="flex gap-2">
          <ShimmerSkeleton className="h-8 w-16 rounded-full" />
          <ShimmerSkeleton className="h-8 w-8 rounded-full" />
        </div>
      </div>
      <div className="flex flex-1 overflow-hidden">
        <SidebarSkeleton className="hidden w-72 border-r md:flex" />
        <div className="flex flex-1 flex-col">
          <ChatMessagesSkeleton />
        </div>
      </div>
    </div>
  );
}

/** Sidebar conversation list skeleton. */
export function SidebarSkeleton({ className }: { className?: string }) {
  return (
    <div className={className} aria-label="Loading sidebar">
      <div className="space-y-3 p-3">
        <ShimmerSkeleton className="h-9 w-full rounded-lg" />
        <ShimmerSkeleton className="h-8 w-full rounded-lg" />
        <div className="space-y-2 pt-2">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="flex items-center gap-2 rounded-lg px-2 py-2">
              <ShimmerSkeleton className="h-4 w-4 rounded" />
              <ShimmerSkeleton className="h-4 flex-1" style={{ width: `${60 + (index % 3) * 10}%` }} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/** Auth form field skeleton. */
export function AuthFormSkeleton({ fields = 3 }: { fields?: number }) {
  return (
    <div className="space-y-4" aria-label="Loading form">
      {Array.from({ length: fields }).map((_, index) => (
        <ShimmerSkeleton key={index} className="h-10 w-full rounded-md" />
      ))}
      <ShimmerSkeleton className="h-10 w-full rounded-md" />
    </div>
  );
}

/** OTP input skeleton. */
export function OtpFormSkeleton() {
  return (
    <div className="space-y-4" aria-label="Loading verification">
      <div className="flex justify-center gap-2">
        {Array.from({ length: 6 }).map((_, index) => (
          <ShimmerSkeleton key={index} className="h-12 w-10 sm:h-14 sm:w-12" />
        ))}
      </div>
      <ShimmerSkeleton className="h-10 w-full" />
    </div>
  );
}

/** Generic dashboard page content skeleton (fits inside DashboardShell). */
export function PageContentSkeleton() {
  return (
    <div className="flex flex-1 flex-col p-4 sm:p-6 lg:p-8" aria-label="Loading page">
      <ShimmerSkeleton className="h-7 w-40" />
      <div className="mt-6 space-y-4">
        <ShimmerSkeleton className="h-32 w-full rounded-xl" />
        <ShimmerSkeleton className="h-32 w-full rounded-xl" />
        <ShimmerSkeleton className="h-24 w-full rounded-xl" />
      </div>
    </div>
  );
}

/** Profile or settings card skeleton. */
export function SettingsPageSkeleton() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 p-4 sm:p-6 lg:p-8" aria-label="Loading settings">
      {Array.from({ length: 3 }).map((_, index) => (
        <div key={index} className="space-y-4 rounded-xl border border-border/60 p-4">
          <ShimmerSkeleton className="h-5 w-32" />
          <SkeletonText lines={2} />
          <div className="flex justify-end">
            <ShimmerSkeleton className="h-8 w-24 rounded-md" />
          </div>
        </div>
      ))}
    </div>
  );
}

