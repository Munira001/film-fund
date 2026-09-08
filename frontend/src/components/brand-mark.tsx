export function BrandMark({
  wordmark = true,
  className = "",
}: {
  wordmark?: boolean;
  className?: string;
}) {
  return (
    <span className={`flex items-center gap-2 ${className}`}>
      <img
        src="/ff-logo.svg"
        alt=""
        width={24}
        height={24}
        className="h-6 w-6"
      />
      {wordmark ? (
        <span className="text-sm font-medium tracking-[-0.2px]">
          FILMFUND
        </span>
      ) : null}
    </span>
  );
}
