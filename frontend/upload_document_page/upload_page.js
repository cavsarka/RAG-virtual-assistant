document.addEventListener("DOMContentLoaded", () => {
    fetchFiles();

    document.getElementById('upload-form').addEventListener('submit', uploadFile);
});

async function fetchFiles() {
    const response = await fetch('http://127.0.0.1:5000/list_files');
    const files = await response.json();
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = ''; // Clear existing list


    if (files.length === 0) {
        ExistingDocs.textContent = "";
    } else {
        ExistingDocs.textContent = "Existing Documents"; // Or any desired default text
        
        files.forEach(file => {
            const listItem = document.createElement('li');
            
            const fileInfo = document.createElement('div');
            fileInfo.className = 'file-info';
            
            const emoji = document.createElement('span');
            emoji.textContent = "📄"; // Use emoji directly
            emoji.className = 'file-icon';
            
            const fileLink = document.createElement('a');
            fileLink.href = `http://127.0.0.1:5000/download_file/${file}`; // URL to download the file
            fileLink.textContent = file;
            fileLink.setAttribute('download', file); // Attribute to trigger download
            fileLink.className = 'file-link'; // Optional: for styling

            fileInfo.appendChild(emoji);
            fileInfo.appendChild(fileLink);

            const deleteButton = document.createElement('button');
            deleteButton.textContent = '🗑️';
            deleteButton.className = 'delete-button';
            
            // Add confirmation dialog before deleting
            deleteButton.onclick = () => {
                if (confirm(`Are you sure you want to delete ${file}?`)) {
                    deleteFile(file);
                }
            };

            listItem.appendChild(fileInfo);
            listItem.appendChild(deleteButton);
            fileList.appendChild(listItem);
        });
    }
}

async function uploadFile(event) {

    event.preventDefault(); // Prevent default form submission

    const formData = new FormData();
    const fileInput = document.getElementById('file-upload');

    if (!fileInput.files.length) {
        fileInput.click(); // Trigger the file input click
        return;
    }
    

    formData.append('file', fileInput.files[0]);

    const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        alert('File uploaded successfully!');
        fileInput.value = "";
        fetchFiles(); // Refresh the list of files
    } else {
        alert('Failed to upload file.');
    }
}

async function deleteFile(filename) {
    const response = await fetch('http://127.0.0.1:5000/delete_file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename }),
    });
    
    fetchFiles();

    // if (response.ok) {
    //     alert('File deleted successfully!');
    //     fetchFiles(); // Refresh the list of files
    // } else {
    //     alert('Failed to delete file.');
    // }
}
