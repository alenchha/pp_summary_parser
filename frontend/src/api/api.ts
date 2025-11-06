const API_URL = import.meta.env.VITE_BACKEND_URL;

type GeneratePdfPayload = {
  request_id: string;
  images_data: unknown[];
  title: string;
};

export async function uploadImages(files: FileList | File[]) {
    const formData = new FormData();

    Array.from(files).forEach((file) => {
        formData.append("files", file);
    });

    const res = await fetch(`${API_URL}/api/upload-images`, {
        method: "POST",
        body: formData,
    });

    return await res.json();
}

export async function generatePdf(payload: GeneratePdfPayload) {
    const res = await fetch(`${API_URL}/api/generate-pdf`, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
});


return await res.json();
}

export async function downloadPdf(filename: string) {
    const res = await fetch(`${API_URL}/api/download-pdf/${filename}`);
    const blob = await res.blob();

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
