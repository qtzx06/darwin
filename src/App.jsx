import './App.css'

function App() {
  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      margin: 0,
      padding: 0,
      overflow: 'hidden'
    }}>
      <iframe
        src="/wisp/index.html"
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
          display: 'block'
        }}
        title="Wisp Animation"
      />
    </div>
  )
}

export default App
