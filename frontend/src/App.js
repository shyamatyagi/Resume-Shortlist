import React, { useState } from "react";
import axios from "axios";

function App() {
  const [files, setFiles] = useState([]);
  const [requirement, setRequirement] = useState("");
  const [results, setResults] = useState([]);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files).slice(0, 10);
    setFiles(selectedFiles);
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
        <span style={{ marginLeft: 8, marginRight: 8, color: "gray" }}>
          (Max 10 PDFs)
        </span>
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
        <table
          style={{ width: "100%", marginTop: 16, borderCollapse: "collapse" }}
        >
          <thead>
            <tr>
              <th style={{ border: "1px solid #ccc", padding: 8 }}>Rank</th>
              <th style={{ border: "1px solid #ccc", padding: 8 }}>
                File Name
              </th>
              <th style={{ border: "1px solid #ccc", padding: 8 }}>
                Similarity (%)
              </th>
              <th style={{ border: "1px solid #ccc", padding: 8 }}>Domain</th>
            </tr>
          </thead>
          <tbody>
            {results
              .sort((a, b) => b.match - a.match)
              .map((r, i) => (
                <tr key={i}>
                  <td style={{ border: "1px solid #ccc", padding: 8 }}>
                    {i + 1}
                  </td>
                  <td style={{ border: "1px solid #ccc", padding: 8 }}>
                    {r.name}
                  </td>
                  <td style={{ border: "1px solid #ccc", padding: 8 }}>
                    {r.match}
                  </td>
                  <td style={{ border: "1px solid #ccc", padding: 8 }}>
                    {r.best_title || "-"}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
