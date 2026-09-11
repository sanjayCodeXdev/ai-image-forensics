import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ScanSearch } from 'lucide-react'
import ProgressSteps from '../components/ProgressSteps'
import { getAnalysis } from '../services/api'

const STEP_IDS = ['upload','metadata','provenance','watermark','visual','forensics','fusion']
const STEP_MS  = [500, 800, 600, 600, 1200, 1500, 700]  // simulated durations per step

export default function Loading() {
  const { analysisId } = useParams()
  const navigate       = useNavigate()
  const [currentStep, setCurrentStep] = useState(STEP_IDS[0])
  const timerRef = useRef(null)

  useEffect(() => {
    // If we have an analysisId, poll the API until the record exists
    // Meanwhile animate through steps as a visual UX
    let stepIdx = 0
    let elapsed = 0

    const tick = () => {
      elapsed += STEP_MS[stepIdx]
      stepIdx++
      if (stepIdx < STEP_IDS.length) {
        setCurrentStep(STEP_IDS[stepIdx])
        timerRef.current = setTimeout(tick, STEP_MS[stepIdx])
      }
    }
    timerRef.current = setTimeout(tick, STEP_MS[0])

    // If analysisId already provided → result is ready, just animate briefly
    if (analysisId) {
      const checkReady = async () => {
        try {
          await getAnalysis(analysisId)
          // Analysis exists — navigate to results after short delay
          setTimeout(() => navigate(`/results/${analysisId}`, { replace: true }), 1500)
        } catch {
          // Not ready yet, wait
          setTimeout(checkReady, 2000)
        }
      }
      checkReady()
    }

    return () => clearTimeout(timerRef.current)
  }, [analysisId, navigate])

  return (
    <div className="max-w-xl mx-auto px-4 py-16 text-center space-y-10 animate-fade-in">
      {/* Spinner icon */}
      <div className="flex justify-center">
        <div className="relative w-20 h-20">
          <div className="absolute inset-0 border-4 border-primary-600/20 rounded-full" />
          <div className="absolute inset-0 border-4 border-t-primary-500 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin" />
          <div className="absolute inset-3 flex items-center justify-center">
            <ScanSearch className="w-7 h-7 text-primary-400 animate-pulse" />
          </div>
        </div>
      </div>

      <div>
        <h1 className="text-2xl font-bold text-slate-100">Analysing Image</h1>
        <p className="text-slate-400 text-sm mt-1">
          Running {STEP_IDS.length}-stage forensic pipeline…
        </p>
      </div>

      <ProgressSteps currentStep={currentStep} />

      <p className="text-xs text-slate-600">
        Analysis typically completes in 5–30 seconds depending on image size and
        whether the AI model is configured.
      </p>
    </div>
  )
}
