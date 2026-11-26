"use strict";

const form = document.querySelector("form");
const tien = document.querySelector("#tien");
const loi = document.querySelector("#loi");
const bao = document.querySelector("#bao");
const thuLai = document.querySelector("#thu-lai");
const nutMo = form.querySelector("button");

function kiemTien() {
    const raw = tien.value;
    let message = "";
    if (!raw) message = "Hãy nhập tiền đầu ca.";
    else if (!/^\d+$/.test(raw)) message = "Nhập số nguyên từ 0 trở lên.";
    else if (BigInt(raw) > 9223372036854775807n) message = "Số tiền vượt giới hạn lưu trữ.";
    loi.textContent = message;
    tien.setAttribute("aria-invalid", String(Boolean(message)));
    return !message;
}

async function capNhat(options) {
    nutMo.disabled = true;
    thuLai.hidden = true;
    try {
        const response = await fetch("/api/ca", options);
        const data = await response.json();
        if (!response.ok && !(response.status === 409 && data.ca)) {
            throw new Error(data.loi || "Chưa thể kết nối tới dịch vụ ca thu ngân.");
        }
        form.hidden = Boolean(data.ca);
        document.querySelector("section").hidden = !data.ca;
        bao.textContent = data.loi || (options ? "Đã mở ca." : "");
        if (data.ca) {
            document.querySelector("#ma").textContent = data.ca.ma_ca;
            document.querySelector("#nguoi").textContent = data.ca.nguoi_mo;
            document.querySelector("#dau").textContent =
                BigInt(data.ca.tien_dau).toLocaleString("vi-VN") + " đ";
        }
    } catch (error) {
        form.hidden = true;
        bao.textContent = error instanceof TypeError ? "Mất kết nối tới máy chủ." : error.message;
        thuLai.hidden = false;
    } finally {
        nutMo.disabled = false;
    }
}

tien.addEventListener("input", kiemTien);
form.addEventListener("submit", event => {
    event.preventDefault();
    if (!kiemTien()) {
        tien.focus();
        return;
    }
    if (nutMo.disabled) return;
    // Gửi số nguyên JSON chính xác ngay cả khi vượt độ chính xác của Number.
    capNhat({method: "POST", headers: {"Content-Type": "application/json"},
             body: '{"tien_dau":' + BigInt(tien.value).toString() + '}'});
});
thuLai.addEventListener("click", () => capNhat());
capNhat();
