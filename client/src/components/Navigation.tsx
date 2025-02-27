import { useState } from "react";
import Output from "./ui/Output";
import AudioStreamer from "./audio/AudioStreamer";

const VerticalTabs = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [outputData, setOutputData] = useState("");

  const tabs = [
    { title: "Microphone", type: "text" },
    { title: "Audio File", type: "data" },
    { title: "Youtube", type: "image" },
  ];

  const handleProcessData = (data) => {
    setOutputData(JSON.stringify(data, null, 2));
  };

  return (
<div className="bg-white">
      {/* Horizontal Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex">
          {tabs.map((tab, index) => (
            <button
              key={index}
              onClick={() => setActiveTab(index)}
              className={`px-4 py-2 text-sm font-medium transition-colors duration-200
                ${activeTab === index 
                  ? 'border-b-2 border-blue-500 text-blue-600' 
                  : 'text-gray-600 hover:text-gray-900 hover:border-gray-300 border-b-2 border-transparent'
                }`}
            >
              {tab.title}
            </button>
          ))}
        </div>
      </div>

      {/* Content Area */}
      <div className="grid grid-cols-2 divide-x divide-gray-200 h-[400px]">
        {/* Input Section */}
        <div className="p-3">
          <h2 className="text-sm font-medium mb-2">{tabs[activeTab].title} Input</h2>
          <div className="space-y-2">
            {/* Input Field */}
            <div>
              {activeTab === 0 && (
                <AudioStreamer />
              )}
              {(activeTab === 1 || activeTab === 2) && (
                <input
                  type="file"
                  accept={activeTab === 2 ? "image/*" : undefined}
                  className="w-full text-sm"
                />
              )}
              {activeTab === 3 && (
                <textarea
                  className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 h-24 font-mono"
                  placeholder="Paste code..."
                />
              )}
            </div>

            {/* Options */}
            <select className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500">
              <option>Option 1</option>
              <option>Option 2</option>
              <option>Option 3</option>
            </select>

            {/* Process Button */}
            <button
              className="w-full px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              onClick={() => handleProcessData("Sample data")}
            >
              Process
            </button>
          </div>
        </div>
        {/* Output Section */}
        < Output />
      </div>
    </div>
  );
};

export default VerticalTabs;
