// static/js/script.js
// Script ini menangani interaksi frontend, unggahan file, tampilan hasil, dan log kinerja.

console.log("script.js berhasil dimuat!");

document.addEventListener("DOMContentLoaded", function () {
  // Mengambil referensi ke elemen-elemen DOM yang akan dimanipulasi
  const uploadForm = document.getElementById("uploadForm");
  const statusDiv = document.getElementById("status");
  const loadingSpinner = document.getElementById("loadingSpinner");
  const imageResultsDiv = document.getElementById("imageResults");
  const llmResultTextDiv = document.getElementById("llmResultText");
  const llmResultImageDiv = document.getElementById("llmResultImage");
  const logTableContainer = document.getElementById("logTableContainer");
  const downloadLogBtn = document.getElementById("downloadLogBtn");
  const clearLogBtn = document.getElementById("clearLogBtn");

  /**
   * Memperbarui pesan status di UI dan mengontrol visibilitas spinner loading.
   * @param {string} message - Pesan yang akan ditampilkan.
   * @param {boolean} isError - True jika pesan adalah error, False jika bukan.
   * @param {boolean} showSpinner - True untuk menampilkan spinner, False untuk menyembunyikan.
   */
  function updateStatus(message, isError = false, showSpinner = false) {
    statusDiv.textContent = message;
    statusDiv.style.color = isError ? "#D32F2F" : "var(--secondary-color)";
    loadingSpinner.style.display = showSpinner ? "block" : "none";
    // Mengubah warna status menjadi warna sukses jika bukan error dan spinner tidak aktif
    if (!isError && !showSpinner) {
      statusDiv.style.color = "var(--primary-color)";
    }
  }

  /**
   * Memuat ulang tabel log kinerja di UI dengan data terbaru.
   * @param {Array<Object>} logs - Array objek log kinerja.
   */
  function loadPerformanceLogs(logs) {
    console.log("Memuat log kinerja ke UI:", logs); // Debugging di konsol browser
    if (!logs || logs.length === 0) {
      logTableContainer.innerHTML = "<p>Belum ada log kinerja.</p>";
      return;
    }

    let tableHtml = '<table class="performance-table"><thead><tr>';
    // Membuat header tabel dari kunci objek log pertama
    const headers = Object.keys(logs[0]);
    headers.forEach((header) => {
      tableHtml += `<th>${header}</th>`;
    });
    tableHtml += "</tr></thead><tbody>";

    // Mengisi baris tabel dengan data log
    logs.forEach((log) => {
      tableHtml += "<tr>";
      headers.forEach((header) => {
        // Menggunakan atribut data-label untuk responsifitas tabel di perangkat mobile
        tableHtml += `<td data-label="${header}">`;
        if (log[header] === null || log[header] === undefined) {
          tableHtml += "N/A"; // Tampilkan 'N/A' jika data kosong
        } else {
          let displayValue = String(log[header]);
          // Memotong teks jika terlalu panjang agar tabel tidak melebar
          if ((header === "LLM Prompt" || header === "LLM Response (Partial)" || header === "Status Message") && displayValue.length > 50) {
            displayValue = displayValue.substring(0, 50) + "...";
          }
          tableHtml += displayValue;
        }
        tableHtml += "</td>";
      });
      tableHtml += "</tr>";
    });
    tableHtml += "</tbody></table>";
    logTableContainer.innerHTML = tableHtml; // Memperbarui konten tabel di DOM
  }

  // Memuat log kinerja saat halaman pertama kali dimuat
  // Data `performance_logs` datang dari Flask melalui Jinja2 rendering
  // `initialPerformanceLogs` adalah variabel global yang diasumsikan ada di `index.html`
  if (typeof initialPerformanceLogs !== "undefined" && initialPerformanceLogs.length > 0) {
    loadPerformanceLogs(initialPerformanceLogs);
  }

  // Event listener untuk tombol "Unduh Log Kinerja"
  if (downloadLogBtn) {
    downloadLogBtn.addEventListener("click", function () {
      // Mengarahkan browser untuk mengunduh file log dari rute Flask
      window.location.href = "/download-performance-log";
    });
  }

  // Event listener untuk tombol "Bersihkan Log Kinerja"
  if (clearLogBtn) {
    clearLogBtn.addEventListener("click", async function () {
      // Konfirmasi pengguna sebelum menghapus log
      if (confirm("Apakah Anda yakin ingin menghapus semua log kinerja? Aksi ini tidak dapat dibatalkan.")) {
        updateStatus("Membersihkan log kinerja...", false, true); // Tampilkan status loading
        try {
          // Mengirim permintaan POST ke rute Flask untuk menghapus log
          const response = await fetch("/clear-performance-log", {
            method: "POST",
          });
          const result = await response.json(); // Menerima respons JSON dari server
          if (response.ok) {
            updateStatus(result.message, false, false); // Tampilkan pesan sukses
            loadPerformanceLogs(result.performance_log); // Muat log yang diperbarui (seharusnya kosong)
          } else {
            updateStatus(`Error: ${result.error || "Gagal membersihkan log."}`, true, false); // Tampilkan pesan error
            loadPerformanceLogs(result.performance_log); // Muat log yang ada (jika gagal hapus)
          }
        } catch (error) {
          console.error("Error saat membersihkan log:", error);
          updateStatus("Terjadi kesalahan saat membersihkan log.", true, false);
        }
      }
    });
  }

  // Event listener untuk form unggah file
  if (uploadForm) {
    uploadForm.addEventListener("submit", async function (event) {
      event.preventDefault(); // Mencegah pengiriman form default

      // Reset UI dan tampilkan status inisialisasi
      updateStatus("Menginisialisasi...", false, true);
      imageResultsDiv.innerHTML = "";
      llmResultTextDiv.innerHTML = "";
      llmResultImageDiv.innerHTML = "";

      const formData = new FormData(uploadForm); // Membuat objek FormData dari form

      try {
        updateStatus("Mengunggah file ePub dan memproses...", false, true); // Update status
        // Mengirim file ke backend Flask
        const response = await fetch("/upload", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const result = await response.json(); // Menerima respons JSON dari server
          updateStatus(result.message, false, false); // Tampilkan pesan sukses

          // Tampilkan Teks Hasil LLM jika ada
          if (result.llm_response_text && result.llm_response_text !== "Tidak ada respons dari AI." && result.llm_response_text !== "Tidak ada respons yang dihasilkan dari model.") {
            const heading = document.createElement("h2");
            heading.textContent = "Hasil Pemrosesan AI (Teks)";
            llmResultTextDiv.appendChild(heading);
            const preElement = document.createElement("pre");
            preElement.textContent = result.llm_response_text;
            llmResultTextDiv.appendChild(preElement);
          } else {
            llmResultTextDiv.innerHTML = "<p>Tidak ada hasil AI (teks) yang diminta atau dihasilkan.</p>";
          }

          // Tampilkan gambar hasil LLM jika ada
          if (result.llm_image_url) {
            const heading = document.createElement("h2");
            heading.textContent = "Hasil Pemrosesan AI (Gambar)";
            llmResultImageDiv.appendChild(heading);

            const imgElement = document.createElement("img");
            imgElement.src = result.llm_image_url;
            imgElement.alt = "Hasil AI Gemini";
            llmResultImageDiv.appendChild(imgElement);
          } else {
            llmResultImageDiv.innerHTML = "<p>Tidak ada hasil AI (gambar) yang diminta atau dihasilkan.</p>";
          }

          // Tampilkan gambar-gambar konten ePub asli
          if (result.image_urls && result.image_urls.length > 0) {
            const heading = document.createElement("h2");
            heading.textContent = "Konten ePub Asli (Gambar)";
            imageResultsDiv.appendChild(heading);

            result.image_urls.forEach((imageUrl) => {
              const imgElement = document.createElement("img");
              imgElement.src = imageUrl;
              imgElement.alt = "Konversi Gambar ePub";
              imgElement.loading = "lazy"; // Menggunakan lazy loading untuk gambar banyak
              imageResultsDiv.appendChild(imgElement);
            });
            // Scroll ke hasil yang paling relevan
            if (result.llm_response_text && llmResultTextDiv.offsetHeight > 0) {
              llmResultTextDiv.scrollIntoView({ behavior: "smooth", block: "start" });
            } else if (result.llm_image_url && llmResultImageDiv.offsetHeight > 0) {
              llmResultImageDiv.scrollIntoView({ behavior: "smooth", block: "start" });
            } else if (result.image_urls.length > 0 && imageResultsDiv.offsetHeight > 0) {
              imageResultsDiv.scrollIntoView({ behavior: "smooth", block: "start" });
            }
          } else {
            imageResultsDiv.innerHTML = "<p>Tidak ada gambar konten ePub yang dihasilkan.</p>";
          }

          // Muat ulang log kinerja setelah proses selesai
          if (result.performance_log) {
            loadPerformanceLogs(result.performance_log);
          }
        } else {
          // Penanganan error dari respons server
          const errorResult = await response.json();
          updateStatus(`Error: ${errorResult.error || "Terjadi kesalahan yang tidak diketahui."}`, true, false);
          imageResultsDiv.innerHTML = "<p>Gagal mengkonversi file. Silakan coba lagi.</p>";
          llmResultTextDiv.innerHTML = "";
          llmResultImageDiv.innerHTML = "";
          // Muat ulang log kinerja jika ada error
          if (errorResult.performance_log) {
            loadPerformanceLogs(errorResult.performance_log);
          }
        }
      } catch (error) {
        // Penanganan error jaringan atau JavaScript
        console.error("Error saat berkomunikasi dengan server:", error);
        updateStatus("Terjadi kesalahan saat berkomunikasi dengan server. Cek konsol browser.", true, false);
        imageResultsDiv.innerHTML = "";
        llmResultTextDiv.innerHTML = "";
        llmResultImageDiv.innerHTML = "";
      }
    });
  }
});
