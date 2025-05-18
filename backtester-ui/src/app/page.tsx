import Link from 'next/link'

const strategies = [
  { id: 'moving-average', name: 'Moving Average' },
  { id: 'rb-knoxville', name: 'Rb Knoxville' },
]

export default function Home() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Stock Scanning Strategies</h1>
      <ul className="space-y-4">
        {strategies.map((strategy) => (
          <li key={strategy.id} className="border p-4 rounded-lg hover:bg-gray-100">
            <Link href={`/strategies/${strategy.id}`}>
              <span className="text-xl text-blue-600 hover:underline">{strategy.name}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}