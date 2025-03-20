import React, { useState } from "react";
import axios from "axios";

function Certificate({ user }) {
  const [certificateType, setCertificateType] = useState("");
  const [downloadLink, setDownloadLink] = useState("");

  const handleRequestCertificate = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/certificate", {
        university_name: "Your University",
        user_id: user.userId,
        certificate_type: certificateType,
      });

      if (response.data.status === "success") {
        setDownloadLink(response.data.file); // Store the download link
      } else {
        alert("Certificate generation failed!");
      }
    } catch (error) {
      console.error("Error generating certificate:", error);
    }
  };

  return (
    <div>
      <h3>Request Certificate</h3>
      <select value={certificateType} onChange={(e) => setCertificateType(e.target.value)}>
        <option value="">Select Certificate Type</option>
        <option value="bonafide">Bonafide Certificate</option>
        <option value="achievement">Achievement Certificate</option>
      </select>
      <button onClick={handleRequestCertificate}>Generate Certificate</button>

      {downloadLink && (
        <div>
          <p>Certificate generated! Click below to download:</p>
          <a href={`http://127.0.0.1:8000${downloadLink}`} target="_blank" rel="noopener noreferrer">
            Download Certificate
          </a>
        </div>
      )}
    </div>
  );
}

export default Certificate;
