interface SpinnerProps {
  size?: string
  color?: string
}

export default function Spinner({ size = 'h-4 w-4', color = 'border-sky-200 border-t-sky-600' }: SpinnerProps) {
  return <div className={`${size} ${color} animate-spin rounded-full border-2`} />
}
