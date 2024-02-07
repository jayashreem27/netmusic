export default function ServerListItem() {
  return (
    <div className="rounded-md bg-neutral-500 mt-2 h-16 p-2 flex flex-row">
      <div className="w-12 h-12 bg-white rounded-md">

      </div>
      <div className="flex flex-col flex-1 ml-2">
        <h3 className="text-white text-xl">Server Name</h3>
        <h4 className="text-white text-md">Server IP</h4>
      </div>
    </div>
  );
}
