import React, { useState, useEffect } from "react";

interface ModelInfo {
  name: string;
  description: string;
  size: string;
  speed: string;
  english_only: boolean;
}

interface ModelsResponse {
  models: Record<string, ModelInfo>;
  current_model: string;
}

interface Model {
  key: string;
  name: string;
}

interface ModelSelectorProps {
  onModelChange: (model: string, modelInfo: any) => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ onModelChange }) => {
  const [models, setModels] = useState<Model[]>([]);
  const [currentModel, setCurrentModel] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    console.log("Fetching models...");
    setLoading(true);
    setError(null);

    fetch("/api/models")
      .then((response) => {
        console.log("Response received:", response);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data: ModelsResponse) => {
        console.log("Data received:", data);
        // Transform the object into an array of models
        const modelList = Object.entries(data.models).map(([key, info]) => ({
          key,
          name: info.name,
        }));
        setModels(modelList);
        setCurrentModel(data.current_model);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching models:", error);
        setError("Failed to load models. Please try again later.");
        setLoading(false);
      });
  }, []);

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedModel = event.target.value;
    const modelInfo = models.find((model) => model.key === selectedModel);
    if (modelInfo) {
      setCurrentModel(selectedModel);
      onModelChange(selectedModel, modelInfo);
    }
  };

  if (loading) {
    return <div>Loading models...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <div>
      <label
        htmlFor="model-selector"
        className="block text-sm font-medium text-gray-700"
      >
        Select Model
      </label>
      <select
        id="model-selector"
        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
        value={currentModel}
        onChange={handleChange}
      >
        <option value="">Select a model</option>
        {models.map((model) => (
          <option key={model.key} value={model.key}>
            {model.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ModelSelector;
