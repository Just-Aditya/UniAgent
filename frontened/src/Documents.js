import React, { useState, useEffect } from "react";
import axios from "axios";

function Documents({ user }) {
  const [file, setFile] = useState(null);
  const [mentorId, setMentorId] = useState("");
  const [comment, setComment] = useState("");
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    if (user.role === "mentor") {
      axios.get(`http://127.0.0.1:8000/mentor_documents/${user.userId}`)
        .then(res => setDocuments(res.data.documents))
        .catch(err => console.error(err));
    }
  }, [user]);

  const handleFileUpload = async () => {
    if (!file || !mentorId) {
      alert("Please select a file and a mentor.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("mentee_id", user.userId);
    formData.append("mentor_id", mentorId);
    formData.append("comment", comment);

    await axios.post("http://127.0.0.1:8000/upload_document", formData);
    alert("Document uploaded successfully!");
  };

  const handleAddRemark = async (documentName, remark) => {
    await axios.post("http://127.0.0.1:8000/add_remark/", {
      document_name: documentName,
      mentor_id: user.userId,
      remark: remark
    });
    alert("Remark added!");
  };

  return (
    <div>
      <h3>Document Sharing</h3>
      {user.role === "mentee" && (
        <div>
          <input type="file" onChange={(e) => setFile(e.target.files[0])} />
          <input type="text" placeholder="Mentor ID" onChange={(e) => setMentorId(e.target.value)} />
          <input type="text" placeholder="Add a comment" onChange={(e) => setComment(e.target.value)} />
          <button onClick={handleFileUpload}>Upload</button>
        </div>
      )}

      {user.role === "mentor" && (
        <div>
          <h3>Received Documents</h3>
          {documents.map((doc, index) => (
            <div key={index}>
              <p><b>{doc.document_name}</b> from {doc.mentee_id}</p>
              <p>Comment: {doc.comment}</p>
              <input type="text" placeholder="Add remark" onBlur={(e) => handleAddRemark(doc.document_name, e.target.value)} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Documents;
