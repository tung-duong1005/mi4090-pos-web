"use strict";

// Nguồn hàng mẫu cho đến khi có API tra hàng của TV2.
const danhMuc = [
    { ma: "S", ten: "Sữa", donVi: "hộp", donGia: 25000 },
    { ma: "N", ten: "Nước suối", donVi: "chai", donGia: 10000 }
];
const dinhDang = new Intl.NumberFormat("vi-VN");
const tien = giaTri => dinhDang.format(giaTri) + " đ";
const chonHang = document.querySelector("#mat-hang");
const gio = new Map();

for (const hang of danhMuc) {
    chonHang.add(new Option(
        hang.ma + " · " + hang.ten + " · " + tien(hang.donGia) + "/" + hang.donVi, hang.ma
    ));
}

function capNhatTong() {
    let tong = 0n;
    for (const dong of gio.values()) tong += dong.thanhTien;
    document.querySelector("#tong").textContent = tien(tong);
    document.querySelector("#gio-trong").hidden = gio.size > 0;
}

function taoDong(hang) {
    const row = document.querySelector("#mau-dong").content.firstElementChild.cloneNode(true);
    const input = row.querySelector("input");
    const loi = row.querySelector("small");
    const xoa = row.querySelector("button");
    const dong = { input, soLuong: 0n, thanhTien: 0n };
    row.cells[0].textContent = hang.ma;
    row.cells[1].textContent = hang.ten;
    row.cells[2].textContent = tien(hang.donGia) + "/" + hang.donVi;
    loi.id = "loi-" + hang.ma;
    input.setAttribute("aria-label", "Số lượng " + hang.ten);
    input.setAttribute("aria-describedby", loi.id);
    xoa.setAttribute("aria-label", "Xóa " + hang.ten);

    input.addEventListener("input", () => {
        const hopLe = /^\d+$/.test(input.value) && BigInt(input.value) > 0n;
        input.setAttribute("aria-invalid", String(!hopLe));
        loi.textContent = hopLe ? "" : "Nhập số nguyên lớn hơn 0.";
        if (!hopLe) return;
        dong.soLuong = BigInt(input.value);
        dong.thanhTien = dong.soLuong * BigInt(hang.donGia);
        row.cells[4].textContent = tien(dong.thanhTien);
        capNhatTong();
    });
    xoa.addEventListener("click", () => {
        gio.delete(hang.ma);
        row.remove();
        capNhatTong();
        chonHang.focus();
    });
    document.querySelector("#gio-hang").append(row);
    gio.set(hang.ma, dong);
    return dong;
}

document.querySelector("#chon-hang").addEventListener("submit", event => {
    event.preventDefault();
    const hang = danhMuc.find(item => item.ma === chonHang.value);
    const dong = gio.get(hang.ma) ?? taoDong(hang);
    dong.input.value = String(dong.soLuong + 1n);
    dong.input.dispatchEvent(new Event("input"));
});
