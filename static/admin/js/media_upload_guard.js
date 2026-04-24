document.addEventListener("DOMContentLoaded", function () {
  var MAX_BYTES = 4.5 * 1024 * 1024; // conservative guard for Vercel serverless request body limit
  var videoExtensions = ["mp4", "mov", "avi", "wmv", "webm", "flv", "mkv"];

  function isVideo(file) {
    if (!file) return false;

    if (file.type && file.type.toLowerCase().startsWith("video/")) {
      return true;
    }

    var name = (file.name || "").toLowerCase();
    var ext = name.includes(".") ? name.split(".").pop() : "";
    return videoExtensions.includes(ext);
  }

  function formatSize(bytes) {
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  }

  function ensureNoticeContainer(input) {
    var existing = input.parentElement.querySelector(".vercel-upload-warning");
    if (existing) return existing;

    var warning = document.createElement("div");
    warning.className = "help vercel-upload-warning";
    warning.style.color = "#b42318";
    warning.style.fontWeight = "600";
    warning.style.marginTop = "6px";
    input.parentElement.appendChild(warning);
    return warning;
  }

  document.querySelectorAll('input[type="file"]').forEach(function (input) {
    input.addEventListener("change", function () {
      var file = input.files && input.files[0] ? input.files[0] : null;
      if (!file) return;

      var warningNode = ensureNoticeContainer(input);

      if (isVideo(file) && file.size > MAX_BYTES) {
        warningNode.textContent =
          "This video is " +
          formatSize(file.size) +
          ". Vercel serverless uploads may fail above ~4.5 MB with 413 PAYLOAD_TOO_LARGE. Compress the video or host it externally and link it.";
        alert(
          "Video too large for direct Vercel serverless upload. Please compress it to around 4 MB or use an external video URL.",
        );
        input.value = "";
        return;
      }

      warningNode.textContent = "";
    });
  });
});
