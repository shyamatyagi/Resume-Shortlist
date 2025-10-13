import React, { useState } from "react";
import axios from "axios";

function App() {
  const [files, setFiles] = useState([]);
  const [requirement, setRequirement] = useState("");
  const [results, setResults] = useState([]);

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleRequirementChange = (e) => {
    setRequirement(e.target.value);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }
    const res = await axios.post(
      "http://localhost:8000/upload-resumes/",
      formData
    );
    if (res.status === 200 && res.data && res.data.message) {
      alert(res.data.message);
    }
  };

  const handleAddRequirement = async () => {
    const formData = new FormData();
    formData.append("requirement", requirement);
    await axios.post("http://localhost:8000/requirements/", formData);
  };

  const handleShortlist = async () => {
    const res = await axios.get("http://localhost:8000/shortlist/");
    setResults(res.data.results);
  };

  return (
    <div style={{ padding: 32 }}>
      <h1>Resume Shortlisting App</h1>
      <div>
        <input type="file" multiple onChange={handleFileChange} />
        <button onClick={handleUpload}>Upload Resumes</button>
      </div>
      {/* <div style={{ marginTop: 16 }}>
        <input
          type="text"
          value={requirement}
          onChange={handleRequirementChange}
          placeholder="Add requirement"
        />
        <button onClick={handleAddRequirement}>Add Requirement</button>
      </div> */}
      <div style={{ marginTop: 16 }}>
        <button onClick={handleShortlist}>Get Shortlist</button>
        <ul>
          {results.map((r, i) => (
            <li key={i} style={{ color: r.color }}>
              {r.name} - {r.match}%
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
