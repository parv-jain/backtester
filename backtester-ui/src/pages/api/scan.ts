import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios'

type ScanRequest = {
  symbols: string[]
  market: 'US' | 'India'
  strategyName: string
}

export interface ScanResult {
  symbol: string
  buyCondition: boolean
  sellCondition: boolean
  lastPrice?: number
  MA200?: number
  MA50?: number
  MA20?: number
  volume?: number
  date?: string
  error?: string
}

type ScanResponse = ScanResult[]

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ScanResponse>
) {
  if (req.method === 'POST') {
    try {
      const { symbols, market, strategyName } = req.body as ScanRequest
      const response = await axios.post<ScanResponse>('http://localhost:5000/api/scan', { symbols, market, strategyName })
      res.status(200).json(response.data)
    } catch (error: any) {
      res.status(error.status).json(error)
    }
  } else {
    res.setHeader('Allow', ['POST'])
    res.status(405).end(`Method ${req.method} Not Allowed`)
  }
}