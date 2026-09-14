export interface SkeletonProps {
  className?: string;
  "aria-label"?: string;
}

export function Skeleton({ className, ...rest }: SkeletonProps) {
  return <div role="status" className={["skeleton", className].filter(Boolean).join(" ")} {...rest} />;
}
