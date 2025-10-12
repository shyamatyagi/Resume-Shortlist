import React, { useState } from "react";
import axios from "axios";

function Admin() {
  const [csvFile, setCsvFile] = useState(null);
  const [message, setMessage] = useState("");
  const [roles, setRoles] = useState([]);

  const handleFileChange = (e) => {
    setCsvFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!csvFile) return;
    const formData = new FormData();
    formData.append("csv_file", csvFile);
    const res = await axios.post(
      "http://localhost:8000/admin/upload-jobroles/",
      formData
    );
    setMessage(`Added roles: ${res.data.added.join(", ")}`);
    fetchRoles();
  };

  const fetchRoles = async () => {
    const res = await axios.get("http://localhost:8000/admin/jobroles/");
    setRoles(res.data);
  };

  return (
    <div style={{ padding: 32 }}>
      <h1>Admin: Upload Job Roles</h1>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload CSV</button>
      {message && <div style={{ marginTop: 16 }}>{message}</div>}
      <div style={{ marginTop: 32 }}>
        <h2>Job Roles in Database</h2>
        <button onClick={fetchRoles}>Refresh List</button>
        <ul>
          {roles.map((role) => (
            <li key={role.id}>
              <b>{role.title}</b> | Qualification: {role.qualification} |
              Experience: {role.experience} | Techstack: {role.techstack}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Admin;
