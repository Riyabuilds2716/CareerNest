
// =========================
// Search Jobs
// =========================

function searchJobs() {

    let keyword = document.getElementById("jobSearch").value.trim();
    let location = document.getElementById("locationSearch").value.trim();

    // Send search values to Jobs page
    let url = "/jobs?keyword=" + encodeURIComponent(keyword)
                    + "&location=" + encodeURIComponent(location);

    window.location.href = url;
}


// =========================
// Simple Button Message
// =========================

function showMessage() {
    alert("Welcome to Job Portal!");
}

