// material symbols glyph. always decorative: the accessible name comes from
// the visible text or aria-label of the surrounding control.
export function Icon({
  name,
  size = 20,
  fill = false,
  className = "",
}: {
  name: string;
  size?: number;
  fill?: boolean;
  className?: string;
}) {
  return (
    <span
      aria-hidden="true"
      className={`icon ${fill ? "icon-fill" : ""} ${className}`}
      style={{ fontSize: `${size / 16}rem`, width: `${size / 16}rem` }}
    >
      {name}
    </span>
  );
}
