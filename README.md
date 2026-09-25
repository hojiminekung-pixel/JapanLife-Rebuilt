# Japan Life Rebuilt

เกมสร้างเมืองธีมญี่ปุ่นแบบ **clean-room** ที่พัฒนาด้วย Godot 4 สำหรับ Android และเล่นได้แบบออฟไลน์ทั้งหมด. ภาพทั้งหมดในรุ่นนี้เป็นไอคอน Unicode และงาน placeholder ดั้งเดิม; ไม่มีทรัพย์สิน โค้ด หรือระบบจากเกม Japan Life เดิม.

## เริ่มใช้งาน

1. เปิด `project.godot` ด้วย Godot 4.3 หรือใหม่กว่า แล้วกด Run.
2. เลือกช่องว่าง แล้วใช้แถบล่างเพื่อสร้างอาคาร ถนน หรือของตกแต่ง.
3. แตะอาคารเพื่อเก็บรายได้และอัปเกรด. ความคืบหน้าบันทึกใน `user://japan_life_save.json` และคำนวณรายได้ขณะปิดเกม (สูงสุด 8 ชั่วโมง).

ข้อมูล gameplay ที่ขยายได้อยู่ใน `data/*.json`; UI และระบบเกมอยู่ใน `scripts/main.gd`. ฟอนต์ Noto Sans Thai อยู่ใน `assets/fonts/` พร้อมใบอนุญาต SIL Open Font License ใน `licenses/`.

## Android

`export_presets.cfg` ใช้ package id `com.hojiminekung.japanliferebuilt` และมี workflow GitHub Actions ที่ export debug APK แล้วอัปโหลดเป็น artifact.
