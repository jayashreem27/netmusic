import './App.css'
import ServerListItem from './pages/ServerListItem'

function App() {

  return (
    <div className="flex flex-col min-h-screen bg-neutral-950 flex-1">
      <div className="rounded-md bg-neutral-700 mx-2 mt-2 p-1 flex flex-row">
        <h1 className='text-white font-semibold text-3xl'>NetMusic</h1>
      </div>
      <div className="flex-row mx-2 mt-2 flex-1 flex">
        <div className='rounded-md w-1/2 md:w-1/3 lg:w-1/4 2xl:w-1/6 bg-neutral-700 p-2 flex flex-col'>
          <h2 className="text-white text-xl font-semibold">Servers</h2>
          <ServerListItem />
          <ServerListItem />
          <ServerListItem />
          <ServerListItem />

        </div>
        <div className='ml-2 rounded-md flex-1 bg-neutral-700 p-2'>
          <h2 className="text-white text-xl font-semibold">Server</h2>
        </div>
      </div>
      <div className="mx-2 mt-2 flex flex-row flex-1 max-h-16"></div>
    </div>
  )
}

export default App
