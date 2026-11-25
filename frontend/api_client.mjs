// Giữ cùng khoa khi thử lại sau mất kết nối. Chuyển mã ca/phiếu, không gửi vai trò.
export async function guiPhieu(uc, khoa, duLieu) {
    const url = { "02": "/api/ban", "03": "/api/tra" }[uc];
    if (!url) throw new Error("Sai nghiệp vụ");
    const response = await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "Idempotency-Key": khoa },
        body: JSON.stringify(duLieu)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.loi || data.error || String(response.status));
    return data.ma_phieu;
}
