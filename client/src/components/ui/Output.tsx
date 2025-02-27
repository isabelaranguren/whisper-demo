
const Output = () => {
  const outputData = ""; // Define outputData with an initial value
  return (
    <div className="p-3">
      <h2 className="text-sm font-medium mb-2">
         Output
      </h2>
      <div className="bg-gray-50 p-2 rounded border border-gray-200 h-[300px] overflow-auto">
        {outputData ? (
          <pre className="whitespace-pre-wrap text-gray-700 text-sm">
            {outputData}
          </pre>
        ) : (
          <p className="text-gray-500 text-sm">Output will appear here...</p>
        )}
      </div>
    </div>
  );
}

export default Output