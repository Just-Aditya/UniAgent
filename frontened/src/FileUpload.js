import { useState } from "react";

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [downloadLink, setDownloadLink] = useState("");

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            alert("Select a file first!");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://your-backend.com/upload_document/", {
                method: "POST",
                body: formData,
            });

            const result = await response.json();
            if (response.ok) {
                setDownloadLink(result.download_link); // Store the download link
            } else {
                alert("Upload failed!");
            }
        } catch (error) {
            console.error("Upload error:", error);
        }
    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload</button>

            {downloadLink && (
                <p>
                    <a href={downloadLink} target="_blank" rel="noopener noreferrer">
                        Download File
                    </a>
                </p>
            )}
        </div>
    );
};

export default FileUpload;
