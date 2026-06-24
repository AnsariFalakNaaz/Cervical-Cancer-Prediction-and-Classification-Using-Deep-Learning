function toggleSection(id) {
    const section = document.getElementById(id);
    section.classList.toggle("hidden");
}

function predict() {
    const input = document.getElementById("imageInput");
    const file = input.files[0];

    if (!file) {
        alert("Please select an image first.");
        return;
    }

    const preview = document.getElementById("previewImage");
    preview.src = URL.createObjectURL(file);

    const formData = new FormData();
    formData.append("file", file);

    fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {

        const resultCard = document.getElementById("resultCard");
        const className = document.getElementById("className");
        const confidence = document.getElementById("confidence");
        const precautionsSection = document.getElementById("precautionsSection");
        const hospitalsSection = document.getElementById("hospitalsSection");

        resultCard.classList.remove("hidden");

        className.innerText = data.predicted_class;
        confidence.innerText = "Confidence: " + (data.confidence * 100).toFixed(2) + "%";

        if (data.predicted_class.includes("normal")) {
            className.className = "green";
        } else {
            className.className = "red";
        }

        // -------- PRECAUTIONS --------
        precautionsSection.innerHTML = `
            <p><b>Immediate Action:</b> ${data.precautions.immediate_action}</p>
            <p><b>Lifestyle Changes:</b> ${data.precautions.lifestyle_changes}</p>
            <p><b>Follow Up:</b> ${data.precautions.follow_up}</p>
        `;

        // -------- HOSPITALS --------
        if (!data.hospitals || data.hospitals.length === 0) {
            hospitalsSection.innerHTML = "<p style='color:green;'>No hospital visit required.</p>";
        } else {
            hospitalsSection.innerHTML = data.hospitals.map(h => `
                <div style="
                    background:#fff;
                    padding:15px;
                    margin-bottom:15px;
                    border-radius:10px;
                    box-shadow:0 4px 10px rgba(0,0,0,0.1);
                ">
                    <h4 style="margin:0; color:#b30000;">${h.name}</h4>
                    <p><b>Address:</b> ${h.address}</p>
                    <p><b>Doctors:</b> ${h.doctors.join(", ")}</p>
                </div>
            `).join("");
        }

    })
    .catch(error => {
        alert("Error occurred!");
        console.log(error);
    });
}