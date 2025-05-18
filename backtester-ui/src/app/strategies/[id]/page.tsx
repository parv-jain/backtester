"use client";

import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import axios from 'axios'
import Link from 'next/link'
import { ScanResult } from '@/pages/api/scan';

const NASDAQ100 = "AAPL,ABNB,ADBE,ADI,ADP,ADSK,AEP,AMAT,AMD,AMGN,AMZN,ANSS,ARM,ASML,AVGO,AZN,BIIB,BKNG,BKR,CCEP,CDNS,CDW,CEG,CHTR,CMCSA,COST,CPRT,CRWD,CSCO,CSGP,CSX,CTAS,CTSH,DASH,DDOG,DLTR,DXCM,EA,EXC,FANG,FAST,FTNT,GEHC,GFS,GILD,GOOG,GOOGL,HON,IDXX,ILMN,INTC,INTU,ISRG,KDP,KHC,KLAC,LIN,LRCX,LULU,MAR,MCHP,MDB,MDLZ,MELI,META,MNST,MRNA,MRVL,MSFT,MU,NFLX,NVDA,NXPI,ODFL,ON,ORLY,PANW,PAYX,PCAR,PDD,PEP,PYPL,QCOM,REGN,ROP,ROST,SBUX,SMCI,SNPS,TEAM,TMUS,TSLA,TTD,TTWO,TXN,VRSK,VRTX,WBD,WDAY,XEL,ZS"
const NIFTY50 = "ADANIENT,ADANIPORTS,APOLLOHOSP,ASIANPAINT,AXISBANK,BAJAJ-AUTO,BAJFINANCE,BAJAJFINSV,BPCL,BHARTIARTL,BRITANNIA,CIPLA,COALINDIA,DIVISLAB,DRREDDY,EICHERMOT,GRASIM,HCLTECH,HDFCBANK,HDFCLIFE,HEROMOTOCO,HINDALCO,HINDUNILVR,ICICIBANK,ITC,INDUSINDBK,INFY,JSWSTEEL,KOTAKBANK,LTIM,LT,M&M,MARUTI,NTPC,NESTLEIND,ONGC,POWERGRID,RELIANCE,SBILIFE,SHRIRAMFIN,SBIN,SUNPHARMA,TCS,TATACONSUM,TATAMOTORS,TATASTEEL,TECHM,TITAN,ULTRACEMCO,WIPRO"

export default function StrategyScanner() {
  const [symbols, setSymbols] = useState<string>('')
  const [results, setResults] = useState<ScanResult[]>([])
  const [strategyName, setStrategyName] = useState<string>('')
  const [stockMarket, setStockMarket] = useState<'US' | 'India'>('US')
  const id = usePathname();

  function extractStrategy(path: string): string {
    return path.split('/').pop() || '';
  }
  
  useEffect(() => {
    if (id) {
      setStrategyName(extractStrategy(id));
    }
  }, [id])

  const handleScan = async () => {
    try {
      const response = await axios.post<ScanResult[]>('/api/scan', {
        symbols: symbols.split(',').map(s => s.trim()),
        market: stockMarket,
        strategyName,
      })
      setResults(response.data)
    } catch (error) {
      console.error('Error scanning:', error)
    }
  }

  const handleQuickList = (list: string) => {
    setSymbols(list)
  }

  const handleMarketChange = (market: 'US' | 'India') => {
    setStockMarket(market)
    setSymbols('') // Clear textarea when market is changed
  }

  return (
    <div className="container mx-auto p-4">
      <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
        ← Back to Strategies
      </Link>
      <h1 className="text-2xl font-bold mb-4">{strategyName} Scanner</h1>
      
      <div className="mb-4">
        <label className="block mb-2 font-bold">Select Stock Market:</label>
        <select 
          value={stockMarket} 
          onChange={(e) => handleMarketChange(e.target.value as 'US' | 'India')}
          className="p-2 border rounded"
        >
          <option value="US">US Stocks</option>
          <option value="India">Indian Stocks</option>
        </select>
      </div>
      
      <div className="mb-4">
        <label className="block mb-2 font-bold">Quick List:</label>
        {stockMarket === 'US' ? (
          <button 
            onClick={() => handleQuickList(NASDAQ100)} 
            className="px-4 py-2 bg-green-500 text-white rounded"
          >
            NASDAQ 100
          </button>
        ) : (
          <button 
            onClick={() => handleQuickList(NIFTY50)} 
            className="px-4 py-2 bg-green-500 text-white rounded"
          >
            NIFTY 50
          </button>
        )}
      </div>
      
      <textarea
        className="w-full p-2 border rounded"
        value={symbols}
        onChange={(e) => setSymbols(e.target.value)}
        placeholder="Enter stock symbols (comma-separated)"
        rows={5}
      />
      <button 
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
        onClick={handleScan}
      >
        Scan
      </button>
      
      <h2 className="text-xl font-semibold mt-4 mb-2">Results:</h2>
      {results.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-300">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-2 text-left">Symbol</th>
                <th className="px-4 py-2 text-left">Buy Signal</th>
                <th className="px-4 py-2 text-left">Sell Signal</th>
                <th className="px-4 py-2 text-right">Last Price</th>
                <th className="px-4 py-2 text-right">MA200</th>
                <th className="px-4 py-2 text-right">MA50</th>
                <th className="px-4 py-2 text-right">MA20</th>
                <th className="px-4 py-2 text-right">Volume</th>
                <th className="px-4 py-2 text-left">Date</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result, index) => (
                <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                  <td className="px-4 py-2 font-medium">{result.symbol}</td>
                  <td className="px-4 py-2">
                    {result.error ? (
                      <span className="text-red-500">{result.error}</span>
                    ) : (
                      <span className={result.buyCondition ? "text-green-500" : "text-red-500"}>
                        {result.buyCondition ? 'Meets condition' : 'Does not meet'}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2">
                    {result.error ? (
                      <span className="text-red-500">{result.error}</span>
                    ) : (
                      <span className={result.sellCondition ? "text-green-500" : "text-red-500"}>
                        {result.sellCondition ? 'Meets condition' : 'Does not meet'}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2 text-right">{result.lastPrice?.toFixed(2)}</td>
                  <td className="px-4 py-2 text-right">{result.MA200?.toFixed(2)}</td>
                  <td className="px-4 py-2 text-right">{result.MA50?.toFixed(2)}</td>
                  <td className="px-4 py-2 text-right">{result.MA20?.toFixed(2)}</td>
                  <td className="px-4 py-2 text-right">{result.volume?.toLocaleString()}</td>
                  <td className="px-4 py-2">{result.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}