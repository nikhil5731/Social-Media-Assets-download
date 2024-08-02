import { useState } from "react";
import axios from "axios";

const Loader = () => (
  <div className="flex items-center justify-center">
    <div className="loader"></div>
  </div>
);

function App() {
  const [url, setUrl] = useState("");
  const [message, setMessage] = useState("");
  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState(false); // Loader state

  const handleDownload = async () => {
    setLoading(true); // Show loader
    setMessage("");
    setFileName("");

    try {
      const response = await axios.post("http://localhost:8000/download/", { url });
      setMessage(response.data.message);
      setFileName(response.data.file_name);
    } catch (error) {
      setMessage("Error downloading video");
    } finally {
      setLoading(false); // Hide loader
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md">
        <h1 className="text-2xl font-bold mb-4">YouTube Video Downloader</h1>
        <input
          type="text"
          placeholder="Enter YouTube URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="border p-2 w-full mb-4"
        />
        <button
          onClick={handleDownload}
          className="bg-blue-500 text-white py-2 px-4 rounded"
        >
          Download
        </button>
        
        {loading ? ( // Show loader while loading
          <Loader />
        ) : (
          <>
            {message && <p className="mt-4">{message}</p>}
            {fileName && (
              <a
                href={`http://localhost:8000/downloads/${fileName}`}
                className="mt-4 text-blue-500"
                download
                target="__blank"
              >
                Download {fileName}
              </a>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default App;
