// material symbols glyph. always decorative: the accessible name comes from
// the visible text or aria-label of the surrounding control. the ligature name is
// drawn by ::before (globals.css) so it never lands in innerText ("czytaj na głos", copy).
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
      data-icon={name}
      className={`icon ${fill ? "icon-fill" : ""} ${className}`}
      style={{ fontSize: `${size / 16}rem`, width: `${size / 16}rem` }}
    />
  );
}
