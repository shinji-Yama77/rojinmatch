import { useState, useEffect, useRef } from 'react'
import './App.css'

interface Transcript {
  speaker: string;
  text: string;
  is_unsafe: boolean;
  conference_sid: string;
  timestamp: string;
}

interface Alert {
  severity: string;
  message: string;
  context: Transcript;
  timestamp: string;
}

function App() {
  const [queueCount, setQueueCount] = useState(0)
  const [transcripts, setTranscripts] = useState<Transcript[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [connectionStatus, setConnectionStatus] = useState('Disconnected')
  const [activeConference, setActiveConference] = useState<string | null>(null)
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    // Connect to WebSocket
    ws.current = new WebSocket('ws://localhost:8001/ws/dashboard')

    ws.current.onopen = () => {
      setConnectionStatus('Connected')
      console.log('Connected to WebSocket')
    }

    ws.current.onclose = () => {
      setConnectionStatus('Disconnected')
      console.log('Disconnected from WebSocket')
    }

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('Received:', data)

      if (data.event === 'queue_update') {
        setQueueCount(data.count)
      } else if (data.event === 'match_found') {
        // Optional: show notification
      } else if (data.event === 'conference_started') {
        setActiveConference(data.conference_sid)
        // Clear previous transcripts for new conference
        setTranscripts([])
        setAlerts([])
      } else if (data.event === 'transcript') {
        setTranscripts(prev => [...prev, { ...data, timestamp: new Date().toLocaleTimeString() }])
      } else if (data.event === 'alert') {
        setAlerts(prev => [...prev, { ...data, timestamp: new Date().toLocaleTimeString() }])
      }
    }

    return () => {
      ws.current?.close()
    }
  }, [])

  return (
    <div className="container">
      <header>
        <h1>Rojin Caretaker Dashboard</h1>
        <div className={`status ${connectionStatus.toLowerCase()}`}>
          {connectionStatus}
        </div>
      </header>

      <main>
        <div className="stats-panel">
          <div className="card">
            <h2>Queue Size</h2>
            <div className="big-number">{queueCount}</div>
          </div>
          <div className="card">
            <h2>Active Conference</h2>
            <div className="conference-id">{activeConference || 'None'}</div>
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="transcripts-panel">
            <h2>Live Transcripts</h2>
            <div className="scroll-area">
              {transcripts.length === 0 && <p className="placeholder">Waiting for conversation...</p>}
              {transcripts.map((t, i) => (
                <div key={i} className={`transcript-item ${t.is_unsafe ? 'unsafe' : ''}`}>
                  <span className="timestamp">{t.timestamp}</span>
                  <span className="speaker">{t.speaker}:</span>
                  <span className="text">{t.text}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="alerts-panel">
            <h2>Safety Alerts</h2>
            <div className="scroll-area">
              {alerts.length === 0 && <p className="placeholder">No active alerts.</p>}
              {alerts.map((a, i) => (
                <div key={i} className="alert-item">
                  <div className="alert-header">
                    <span className="timestamp">{a.timestamp}</span>
                    <span className="severity">{a.severity.toUpperCase()}</span>
                  </div>
                  <div className="alert-message">{a.message}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
